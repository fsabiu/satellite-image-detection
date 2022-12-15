import flask
from flask_cors import CORS
from flask_api import status
import debugpy
import logging
from flask import request, jsonify
from datetime import datetime
import json
import base64
import sat_utils
from PIL import Image
import tornado.options
import tornado.web

app = flask.Flask(__name__)

CORS(app)

app.config["DEBUG"] = True


debugpy.breakpoint()

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify("pong"), status.HTTP_200_OK

@app.route('/', methods=['GET', 'POST'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''
logging.info('This is an info message')

# A route to return all of the available entries in our catalog.
@app.route('/detect', methods=['POST'])
def detect():
    body = request.get_json(force=True)
    if 'imageData' not in body:
        return jsonify({'response': 'imageData required'}), status.HTTP_400_BAD_REQUEST

    image = body ["imageData"]

    ## from imageHandler
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name = f"img_{timestamp}.{frmt}"
    path = f"images/{name}"

    with open(path, "wb") as fh:
        fh.write(base64.b64decode(image))

    im = Image.open(path)
    w, h = im.size

    size = max(w,h)
    conf = 0.5
    result = sat_utils.detect(path,conf,size)

    return jsonify(result), status.HTTP_200_OK

@app.route('/detectDiff', methods=['POST'])
def detectDiff():
    body = request.get_json(force=True)
    conf = 0.5

    if 'image1' not in body:
        return jsonify({'response': 'image1 missing'}), status.HTTP_400_BAD_REQUEST
    if 'image2' not in body:
        return jsonify({'response': 'image2 missing'}), status.HTTP_400_BAD_REQUEST

    image1 = body ["image1"]
    image2 = body ["image2"]

    ## from imageHandler
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name1 = f"img_{timestamp}_1.{frmt}"
    name2 = f"img_{timestamp}_2.{frmt}"
    path1 = f"images/{name1}"
    path2 = f"images/{name2}"
    
    with open(path1, "wb") as fh:
        fh.write(base64.b64decode(image1))
    with open(path2, "wb") as fh:
        fh.write(base64.b64decode(image2))

    im1 = Image.open(path1)
    im2 = Image.open(path2)

    w1, h1 = im1.size
    w2, h2 = im2.size

    size = max(w1, h1, w2, h2)

    result = sat_utils.detectDiff(path1,path2,conf,size)

    return jsonify(result), status.HTTP_200_OK

@app.route('/detectAllDiff', methods=['POST'])
def detectAllDiff():
    # Default minArea
    minArea = 40
    body = request.get_json(force=True)
    if 'image1' not in body:
        return jsonify({'response': 'image1 missing'}), status.HTTP_400_BAD_REQUEST
    if 'image2' not in body:
        return jsonify({'response': 'image2 missing'}), status.HTTP_400_BAD_REQUEST
    if 'minArea' in body:
        minArea = body["minArea"]

    image1 = body ["image1"]
    image2 = body ["image2"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name1 = f"img_{timestamp}_1.{frmt}"
    name2 = f"img_{timestamp}_2.{frmt}"
    path1 = f"images/{name1}"
    path2 = f"images/{name2}"
    
    with open(path1, "wb") as fh:
        fh.write(base64.b64decode(image1))
    with open(path2, "wb") as fh:
        fh.write(base64.b64decode(image2))

    result = sat_utils.detectAllDiff(path1,path2,minArea)

    return jsonify(result), status.HTTP_200_OK

@app.route('/stitch', methods=['POST'])
def stitch():
    body = request.get_json(force=True)
    if 'image1' not in body:
        return jsonify({'response': 'image1 missing'}), status.HTTP_400_BAD_REQUEST
    if 'image2' not in body:
        return jsonify({'response': 'image2 missing'}), status.HTTP_400_BAD_REQUEST

    image1 = body ["image1"]
    image2 = body ["image2"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name1 = f"img_{timestamp}_1.{frmt}"
    name2 = f"img_{timestamp}_2.{frmt}"
    path1 = f"images/{name1}"
    path2 = f"images/{name2}"

    with open(path1, "wb") as fh:
        fh.write(base64.b64decode(image1))
    with open(path2, "wb") as fh:
        fh.write(base64.b64decode(image2))

    result = sat_utils.stitch(path1,path2)

    return jsonify(result), status.HTTP_200_OK

@app.route('/detectSarDiff', methods=['POST'])
def detectSar():
    body = request.get_json(force=True)
    if 'image1' not in body:
        return jsonify({'response': 'image1 missing'}), status.HTTP_400_BAD_REQUEST
    if 'image2' not in body:
        return jsonify({'response': 'image2 missing'}), status.HTTP_400_BAD_REQUEST

    image1 = body ["image1"]
    image2 = body ["image2"]

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name1 = f"img_{timestamp}_1.{frmt}"
    name2 = f"img_{timestamp}_2.{frmt}"
    path1 = f"images/{name1}"
    path2 = f"images/{name2}"

    #path1 = "/home/oracle/satellite-imgs/Unsupervised-Change-Detection/Data/Dubai_11272000.jpg"
    #path2 = "/home/oracle/satellite-imgs/Unsupervised-Change-Detection/Data/Dubai_11122012.jpg"

    with open(path1, "wb") as fh:
        fh.write(base64.b64decode(image1))
    with open(path2, "wb") as fh:
        fh.write(base64.b64decode(image2))

    result = sat_utils.detectSAR(path1,path2)

    return jsonify(result), status.HTTP_200_OK


app.run(host='0.0.0.0', port=9001, debug=True, ssl_context=('cert/cert.pem', 'cert/ck.pem'))
