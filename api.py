import os
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler

from contours import read_temperatures, read_contours, read_contours_by_level, count_points


app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def hello_world():
    app.logger.info('Hello World')
    return 'Hello, World!'

@app.route('/temperatures')
def temperatures_by_cluster():
    """

        Exemple: http://localhost:5000/temperatures?filepath=res_12.pkl&cluster=spt_8
    """

    args = request.args.to_dict()

    if 'filepath' not in args:
        raise Exception("Parameter filepath is required")

    if 'cluster' not in args:
        raise Exception("Parameter cluster is required")

    data = read_temperatures(args['filepath'], args['cluster'])

    temps = data.tolist()
    temps.sort()
    
    result = dict({
        'cluster': args['cluster'],
        'temperatures': temps,
        'count': len(temps),
    })    
    response = jsonify(result)
    return response

@app.route('/contours_by_temp')
def contours_by_cluster_and_temp():
    """Retorna o contorno para um cluster em uma temperatura expecifica.

    Parameters
    ----------
    filepath : `string`
        Caminho ou nome do arquivo pickle.
    cluster : `string`
        Nome do Cluster dentro do pickle.
    temp : `float`
        Valor da temperatura

    Returns
    ----------
        cluster : `string`
            Nome do Cluster solicitado
        temperature : `string`
            Temperatura solicitada
        contours : `list`
            Lista com os poligonos, cada poligono é um array de RA e Dec em graus.
        count_points : `int`
            Total de pontos, somando todos os poligonos.
        count_polygons : `int`
            Total de poligonos deste contorno.

    Examples
    --------
        http://localhost:5000/contours_by_temp?filepath=res_12.pkl&cluster=spt_8&temp=2.0
    """
    args = request.args.to_dict()

    if 'filepath' not in args:
        raise Exception("Parameter filepath is required")

    if 'cluster' not in args:
        raise Exception("Parameter cluster is required")

    if 'temp' not in args:
        raise Exception("Parameter temp is required")

    curve = read_contours_by_level(args['filepath'], args['cluster'], args['temp'])

    curve_list = [x.tolist() for x in curve]

    count = count_points(curve)
 
    result = dict({
        'cluster': args['cluster'],
        'temperature': args['temp'],
        'count_points': count,
        'count_polygons': len(curve),
        'contours': curve_list,
    })    
    response = jsonify(result)
    return response

@app.route('/contours')
def contours_by_cluster():
    """Retorna todos os contornos para um cluster.

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

    Examples
    --------
        http://localhost:5000/contours?filepath=res_12.pkl&cluster=spt_8
    """
    args = request.args.to_dict()

    if 'filepath' not in args:
        raise Exception("Parameter filepath is required")

    if 'cluster' not in args:
        raise Exception("Parameter cluster is required")

    result = read_contours(args['filepath'], args['cluster'])
    response = jsonify(result)
    return response
    

# TODO: Metodo para retornar o plot em PNG
# TODO: Configurar um Logger.
# TODO: usar MemCache exemplo: https://stackoverflow.com/questions/25176813/how-to-use-flask-cache-and-memcached
# TODO: Colocar no container
# TODO: Usar gunicorn

if __name__ == '__main__':
    # Setup Logger
    handler = RotatingFileHandler('xray_contours.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.DEBUG)
    app.logger.addHandler(handler)

    app.run(host = '0.0.0.0', port=5000, debug=True)