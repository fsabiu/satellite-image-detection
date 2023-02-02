import flask
from flask_cors import CORS
from flask_api import status
import debugpy
import logging
from flask import request, jsonify
from datetime import datetime
import json
import base64
import clu_util
import ml_utils
import report_utils
import sat_utils
from PIL import Image
import os

class ListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, list):
            return obj
        return json.JSONEncoder.default(self, obj)
        
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
    if 'modelId' not in body:
        modelId = 0
    else:
        modelId = body["modelId"]
    if not ml_utils.existsModel(modelId):
        return jsonify({'response': 'model ' + str(modelId) + ' does not exist'}), status.HTTP_400_BAD_REQUEST
    image = body ["imageData"]

    ## from imageHandler
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name = f"{modelId}_img_{timestamp}.{frmt}"
    path = f"images/{name}"

    with open(path, "wb") as fh:
        fh.write(base64.b64decode(image))

    im = Image.open(path)
    w, h = im.size

    size = max(w,h)
    conf = 0.5
    result = sat_utils.detect(path, modelId, conf,size)

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

    with open(path1, "wb") as fh:
        fh.write(base64.b64decode(image1))
    with open(path2, "wb") as fh:
        fh.write(base64.b64decode(image2))
        
    result = sat_utils.detectSAR(path1,path2)

    return jsonify(result), status.HTTP_200_OK

@app.route('/addToTrainingSet', methods=['POST'])
def addToTrainingSet():
    result = {}
    r_status = None
    
    body = request.get_json(force=True)

    if 'modelId' not in body:
        result['response'] = 'modelId missing'
        r_status = status.HTTP_400_BAD_REQUEST
    if 'image' not in body:
        result['response'] = 'image missing'
        r_status = status.HTTP_400_BAD_REQUEST
    if 'objects' not in body:
        result['response'] = 'annotations missing'
        r_status = status.HTTP_400_BAD_REQUEST

    i = 0
    while r_status == None and i < len(body["objects"]):
        if 'x1' not in body["objects"][i]["bounds"] or \
        'y1' not in body["objects"][i]["bounds"] or \
        'x2' not in body["objects"][i]["bounds"] or \
        'y2' not in body["objects"][i]["bounds"] or \
        body["objects"][i]["bounds"]['x2'] < body["objects"][i]["bounds"]['x1'] or \
        body["objects"][i]["bounds"]['y2'] < body["objects"][i]["bounds"]['y1']:
            result['response'] = 'bounds incorrect'
            r_status = status.HTTP_400_BAD_REQUEST
        i = i + 1
    
    if r_status is None:
        image = body["image"]
        objects = body["objects"]
        modelId = body["modelId"]

        if not ml_utils.existsTraining(modelId):
            result['response'] = "Model with id " + str(modelId) + " does not exist"
            r_status = status.HTTP_400_BAD_REQUEST

        if modelId == 0:
            result['response'] = "Please create a new model. You can import model " + str(modelId) + " training data and use it as a base model"
            r_status = status.HTTP_400_BAD_REQUEST

    if r_status is None:
        result = ml_utils.addToTraining(modelId, image, objects)
        r_status = status.HTTP_200_OK
    
    return jsonify(result), r_status

@app.route('/removeFromTrainingSet', methods=['POST'])
def removeFromTraining():
    result = {}
    r_status = None
    body = request.get_json(force=True)

    if 'imageId' not in body:
        result['response'] = 'imageId missing'
        r_status = status.HTTP_400_BAD_REQUEST
    if 'modelId' not in body:
        result['response'] = 'modelId missing'
        r_status = status.HTTP_400_BAD_REQUEST

    if r_status is None:
        imageName = body["imageId"]
        modelId = body["modelId"]

        if not ml_utils.existsTraining(modelId):
            result['response'] = "Model with id " + str(modelId) + " does not exist"
            r_status = status.HTTP_400_BAD_REQUEST

    if r_status is None:
        result = ml_utils.removeFromTraining(modelId, imageName)
        r_status = status.HTTP_200_OK

    return jsonify(result), r_status

@app.route('/getTrainingData', methods=['GET'])
def getTrainingData():
    result = ml_utils.getTrainingData()

    return jsonify(result), status.HTTP_200_OK

@app.route('/getModels', methods=['GET'])
def getModels():
    result = ml_utils.getModels()

    return jsonify(result), status.HTTP_200_OK

@app.route('/getClasses', methods=['POST'])
def getClasses():
    r_status = None

    body = request.get_json(force=True)
    if 'modelId' not in body:
        result['response'] = 'modelId missing'
        r_status = status.HTTP_400_BAD_REQUEST
    else:
        result = ml_utils.getClasses(body["modelId"])
        r_status = status.HTTP_200_OK

    return jsonify(result), status.HTTP_200_OK

@app.route('/createModel', methods=['GET'])
def createModel():
    result = ml_utils.createModel()

    return jsonify(result), status.HTTP_200_OK

@app.route('/deleteModel', methods=['DELETE'])
def delTrainingModels():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    if 'modelId' not in body:
        result['response'] = "modelId missing"
        r_status = status.HTTP_400_BAD_REQUEST
    elif int(body['modelId']) == 0:
        result['response'] = "Cannot delete model 0"
        r_status = status.HTTP_200_OK
    else:
        modelId = body['modelId'] # Check if number
        result, r_status = ml_utils.deleteModel(modelId), status.HTTP_200_OK

    return jsonify(result), r_status

@app.route('/trainModel', methods=['POST'])
def trainModel():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    if 'modelId' not in body:
        result['response'] = "modelId missing"
        r_status = status.HTTP_400_BAD_REQUEST
    else:
        modelId = body['modelId'] # Check if number
        if 'trainingData' in body:
            result['response'] = ml_utils.trainModel(modelId, body["trainingData"])
            r_status = status.HTTP_200_OK
        else:
            result['response'] = ml_utils.trainModel(modelId)
            r_status = status.HTTP_200_OK

    return jsonify(result), r_status

@app.route('/getStatus', methods=['POST'])
def getStatus():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    if 'jobId' not in body:
        result['response'] = "jobId missing"
        r_status = status.HTTP_400_BAD_REQUEST
    else:
        jobId = body['jobId'] # Check if number
        result = ml_utils.getStatus(jobId)
        r_status = status.HTTP_200_OK

    return jsonify(result), r_status

@app.route('/clusterData', methods=['POST'])
def clusterData():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    clu_util.cluster_data()

    result['response'] = 'OK'

    return jsonify(result), r_status

@app.route('/reports/query', methods=['POST'])
def getReports():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    for field in body:
        if field not in list(report_utils.report_fields.values()) + ['x', 'y']:
            result['response'] = "Field " + field + " missing"
            r_status = status.HTTP_400_BAD_REQUEST
    else:
        result = report_utils.query(body)
        r_status = status.HTTP_200_OK

    return jsonify({"reports": result}), r_status

@app.route('/reports/searchAny', methods=['POST'])
def searchInReports():
    result = {}
    r_status = None

    body = request.get_json(force=True)

    if "query" not in body:
        result['response'] = "query parameter missing"
        r_status = status.HTTP_400_BAD_REQUEST
    else:
        result = report_utils.searchInReports(body)
        r_status = status.HTTP_200_OK

    return jsonify({"reports": result}), r_status

@app.route('/reports/tags', methods=['POST'])
def getTags():
    r_status = status.HTTP_200_OK

    filter = ''
    body = request.get_json(force=True)
    if 'query' in body:
        filter = body['query']
    
    result = report_utils.getTags(filter)
    return jsonify({"tags": result}), r_status


def appInit():
    ml_utils.createTrainingTree(0)

    ml_utils.createTrainingTree(1)

    if not os.path.exists("models"):
        os.makedirs("models")

    if not os.path.exists("logs"):
        os.makedirs("logs")

if __name__ == "__main__":
    appInit()
    app.run(host='0.0.0.0', port=9001, debug=True, ssl_context=('cert/cert.pem', 'cert/ck.pem'))


