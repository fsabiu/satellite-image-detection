import flask
from flask_cors import CORS
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
@app.route('/', methods=['GET', 'POST'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''
logging.info('This is an info message')

# A route to return all of the available entries in our catalog.
@app.route('/detect', methods=['POST'])
def api_all():
    body = request.get_json(force=True)
    if 'imageData' not in body:
        self.write_error(400, errorCode=40001, message='imageData not found')

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

    return jsonify(result)

app.run(host='0.0.0.0', port=9001, debug=True, ssl_context=('cert/cert.pem', 'cert/ck.pem'))
