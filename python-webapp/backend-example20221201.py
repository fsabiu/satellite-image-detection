#!/usr/bin/env python
"""
Licensed under the MIT Licence, Copyright (c) 2014 Sinch AB

This demonstrates a basic partner backend for generating authentication tokens. 
In this example the user database is not persistent: Only for demonstrational purpose!
See rows ~100-120 for code on generating a Sinch compatible authentication token.
"""
import sys
#sys.path.insert(0, './detect')
import tornado.ioloop
import tornado.web
from tornado.web import Finish
from datetime import datetime
import json
import uuid
import hmac
import hashlib
import base64
import sat_detect
from PIL import Image
from matplotlib import cm
import numpy as np

# Swagger
import swagger_ui
from apispec import APISpec
from apispec.exceptions import APISpecError
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.tornado import TornadoPlugin


# Port
HTTP_PORT = 2048

# App key + secret
APPLICATION_KEY = 'someUserName'
APPLICATION_SECRET = 'INSERT_YOUR_APP_SECRET_HERE'

userBase = dict()

# Generate Sinch authentication ticket. Implementation of:
# http://www.sinch.com/docs/rest-apis/api-documentation/#Authorization
def getAuthTicket(user): 
    userTicket = {
        'identity': {'type': 'username', 'endpoint': user['username']},
        'expiresIn': 3600, #1 hour expiration time of session when created using this ticket
        'applicationKey': APPLICATION_KEY,
        'created': datetime.utcnow().isoformat()
    }

    userTicketJson = json.dumps(userTicket).replace(" ", "")
    userTicketBase64 = base64.b64encode(userTicketJson)

    # TicketSignature = Base64 ( HMAC-SHA256 ( ApplicationSecret, UTF8 ( UserTicketJson ) ) )
    digest = hmac.new(base64.b64decode(
        APPLICATION_SECRET), msg=userTicketJson, digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(digest)

    # UserTicket = TicketData + ":" + TicketSignature
    signedUserTicket = userTicketBase64 + ':' + signature
    return {'userTicket': signedUserTicket}


# REST endpoints
class PingHandler(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def get(self):
        self.write('pong')


class RestResource(tornado.web.RequestHandler):

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json; charset=UTF-8")

    def write_error(self, status_code, **kwargs):
        data = {}
        for key, value in kwargs.items():
            data[key] = value
        try:
            del data['exc_info']
        except:
            pass

        self.write(json.dumps(data))
        self.set_status(status_code)
        raise Finish()


class satDetectHandler(RestResource):

    def post(self):
        body = json.loads(self.request.body)

        if "confidence" not in body:
            self.write_error(400, errorCode=40001, message='confidence not found')
        if 'imageId' not in body:
            self.write_error(400, errorCode=40001, message='image not found')
        if 'size' not in body:
            self.write_error(400, errorCode=40001, message='size not found')
        
        conf = body["confidence"]
        size = body ["size"]
        id = body ["imageId"]

        img = f"images/{id}"

        result = sat_detect.detect(img,conf,size)

        self.write(json.dumps(result))
"""
       im = Image.fromarray(np.uint8(result.render()[0]))

        im.save("temp/tempImage.jpg")

        with open("temp/tempImage.jpg","rb") as f:
            encodedImage = base64.b64encode(f.read()) 
"""
        


class satImageHandler(RestResource):

    def post(self):
        body = json.loads(self.request.body)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        frmt = body["format"]
        name = f"img_{timestamp}.{frmt}"
        path = f"images/{name}"

        with open(path, "wb") as fh:
            fh.write(base64.b64decode(body["image"]))
        
        self.write(json.dumps(f"id:{name}"))


SWAGGER_API_OUTPUT_FILE = "./swagger.json"

handlers = [
        (r"/ping", PingHandler),
        (r"/detect", satDetectHandler),
        (r"/image", satImageHandler),
    ]

backend = tornado.web.Application(handlers)

def generate_swagger_file(handlers, file_location):
    """Automatically generates Swagger spec file based on RequestHandler
    docstrings and saves it to the specified file_location.
    """

    # Starting to generate Swagger spec file. All the relevant
    # information can be found from here https://apispec.readthedocs.io/
    spec = APISpec(
        title="Satellite images API",
        version="1.0.0",
        openapi_version="3.0.2",
        info=dict(description="Documentation for Satellite images API"),
        plugins=[TornadoPlugin(), MarshmallowPlugin()],
        servers=[
            {"url": "http://localhost:9001/", "description": "Local environment",},
        ],
    )
    # Looping through all the handlers and trying to register them.
    # Handlers without docstring will raise errors. That's why we
    # are catching them silently.
    for handler in handlers:
        try:
            spec.path(urlspec=handler)
        except APISpecError:
            pass

    # Write the Swagger file into specified location.
    with open(file_location, "w", encoding="utf-8") as file:
        json.dump(spec.to_dict(), file, ensure_ascii=False, indent=4)


def make_app():
    # Initialize Tornado application
    app = tornado.web.Application(handlers)

    # Generate a fresh Swagger file
    generate_swagger_file(handlers, SWAGGER_API_OUTPUT_FILE)

    # Start the Swagger UI. Automatically generated swagger.json can also
    # be served using a separate Swagger-service.
    swagger_ui.tornado_api_doc(
        app,
        config_path=SWAGGER_API_OUTPUT_FILE,
        url_prefix="/swagger/spec.html",
        title="Satellite images API",
    )

    return app

if __name__ == "__main__":

    print ("Starting Sinch demo backend on port: \033[1m" + str(HTTP_PORT) +'\033[0m')
    #print ("Application key: \033[1m" + APPLICATION_KEY +'\033[0m')
    #print ("Post JSON object to \033[1m/register\033[0m to create user")
    #print ("Post JSON object to \033[1m/login\033[0m to retrieve authentication token")
    #print ("Example JSON: {username: 'someUserName', password: 'highlySecurePwd'}")
    
    print("Generating swagger...")
    app = make_app()
    app.listen(9001)
    tornado.ioloop.IOLoop.current().start()

    
    print ("--- LOG ---")

    backend.listen(HTTP_PORT)
    tornado.ioloop.IOLoop.instance().start()
