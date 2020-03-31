import pickle as pk

import matplotlib as mpl
import numpy as np
import pylab as plt
from matplotlib import cm


def get_index_by_level(data, level):
    return int(np.where(data['levels'] == float(level))[0][0])


def count_points(curve):
    """
        Conta o total de pontos no contorno de um level especifico. 
        Nesta função, uma curva é um array de poligos, cada poligono é formado por um array de RA e Dec. 
        exemplo de um poligono:
        [[356.26311796 -42.82041983]
        [356.26462934 -42.81989346]
        [356.26628627 -42.81958034]
        [356.26794364 -42.81960402]
        [356.2696012  -42.81976407]
        [356.27125911 -42.82016746]
        [356.27194476 -42.82041343]] 
         
    """
    count = 0
    for polygon in curve:
        count += len(polygon)
    return count

def get_colors(levels):
    colors = np.log10(levels)
    colors = (colors-min(colors))/(max(colors)-min(colors))
    return colors

def plot_cbar(levels, cmap, skip=3):
    colors = get_colors(levels)
    mpb = mpl.cm.ScalarMappable(cmap=cmap)
    mpb.set_array(colors)
    cb = plt.colorbar(mpb)
    cb.set_ticks(colors[::skip])
    cb.set_ticklabels(levels[::skip])

def generate_colorscale(levels):
    """Gera um array com as cores do colorscale do matplotlib
    no formato compativel com a custom colorscale do ploty js https://plotly.com/javascript/colorscales/

    Returns
    ----------
        color value : `float`
        valor da temperatura convertido na escala de cor.

        rgba : `array`
        Cor da temperatura em RGBA

        hex : `string`
        Cor da temperatura em Hex ex: #0088ff
    """
    cmap = mpl.cm.get_cmap('jet')
    colors = get_colors(levels)

    colorscale = list()

    for idx in range(len(levels)):
        # Recupera a cor da temperatura na color scale.
        rgba_color = cmap(colors[idx])

        # Converte a cor de rgba para hex
        hex_color = mpl.colors.to_hex(rgba_color)

        # Guarda as cores na lista colorbar. 
        colorscale.append([colors[idx], rgba_color, hex_color])

    return colorscale

def read_pickle(filepath, cluster):
    try:
        data = pk.load(open(filepath, 'rb'))

        # TODO: os dados do pickle poderiam ficar no Memcache.

        return data[cluster]
    except Exception as e:
        # TODO usar logging
        raise e


def read_temperatures(filepath, cluster):
    try:
        data = read_pickle(filepath, cluster)

        return data['levels']

    except Exception as e:
        # TODO usar logging
        raise e

def read_contours_by_level(filepath, cluster, level):
    try:
        data = read_pickle(filepath, cluster)

        level_idx = get_index_by_level(data, level)

        curves = data['curves'][level_idx]
        
        return curves

    except Exception as e:
        # TODO usar logging
        raise e

def read_contours(filepath, cluster):
    """Le um arquivo de contornos e retorna um objeto que contem a lista de temperaturas, 
    um array de contornos e a colorscale. o retorno deste metodo não possui objetos numpy
    seu resultado pode ser serializado em json. 

    Parameters
    ----------
    filepath : `string`
        Caminho ou nome do arquivo pickle.
    cluster : `string`
        Nome do Cluster dentro do pickle.

    Returns
    ----------

    temperatures : `array`
        Um Array com as temperaturas.
    contours : `array`
        Um array de dicionarios com os dados das curvas
        cara curva está representada desta forma: 
        {
            "index": 0, 
            "temperature": 0,
            "count_polygons": 0, 
            "count_points": 0, 
            "curves": [], 
            "color": "#0000cd", 
        }, 

    colorscales : `array`
        Um Array com o valor da cor na color scale, rgba, hex 
    """
    try:
        # Le o arquivo pickle
        data = read_pickle(filepath, cluster)

        # recuperar todos os levels e todos os contornos.
        all_levels = data['levels']

        # Color Scale
        colorscale = generate_colorscale(all_levels)

        # Para cada temperatura retornar as curvas.
        contours = list()
        for idx in range(len(all_levels)):

            # Recupera a temperatura
            temperature = all_levels[idx]

            # Recuperar as curvas para cada level baseado no index.
            curves_by_level = data['curves'][idx]

            # Converter as curvas de nd.array para listas.
            curve_list = [x.tolist() for x in curves_by_level]

            # Recupera a cor da curva na colorscale.
            hex_color = colorscale[idx][2]

            # Cria um objeto para representar uma curva. 
            curves = dict({
                # Indice desta curva no pickle
                'index': idx,
                # Temperatura desta curva
                'temperature':temperature,
                # Quantidade de poligonos em cada curva
                'count_polygons': len(curves_by_level),
                # Quantidade de pontos nesta curva. 
                'count_points': count_points(curves_by_level),
                # Array de poligonos e suas posições.
                'curves': curve_list, 
                # Cor da curva baseado no color bar do matplotlib
                'color': hex_color
            })

            # Adiciona uma curva a lista de contornos.
            contours.append(curves)


        result = dict({
            'temperatures': all_levels.tolist(),
            'contours': contours,
            'colorscales': colorscale
        })
        return result

    except Exception as e:
        # TODO usar logging
        raise e


# test = pk.load(open('res_12.pkl', 'rb'))
# print(len(test['spt_8']['levels']), len(test['spt_8']['curves']))
# for i in range(3):
#     print(test['spt_8']['levels'][i], '\t',
#           len(test['spt_8']['curves'][i]),
#          [curve.shape for curve in test['spt_8']['curves'][i]])

# def get_levels(vals):
#     colors = np.log10(vals)
#     colors = (colors-min(colors))/(max(colors)-min(colors))
#     return colors

# def plot_cbar(vals, cmap, skip=3):
#     colors = get_levels(vals)
#     mpb = mpl.cm.ScalarMappable(cmap=cmap)
#     mpb.set_array(colors)
#     cb = plt.colorbar(mpb)
#     cb.set_ticks(colors[::skip])
#     cb.set_ticklabels(vals[::skip])

# cmap = mpl.cm.get_cmap('jet')
# for curves, level in zip(test['spt_8']['curves'],
#                          get_levels(test['spt_8']['levels']),
#                         ):
#     for curve in curves:
#         plt.plot(*curve.T, color=cmap(level))
# plot_cbar(test['spt_8']['levels'], cmap)

# plt.savefig('test.png')
