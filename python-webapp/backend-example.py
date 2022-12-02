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
import base64
import sat_utils
from PIL import Image
from matplotlib import cm
import numpy as np
import tornado.options
import tornado.web
from tornado_swagger.setup import setup_swagger


# Port
HTTP_PORT = 2048

# App key + secret
APPLICATION_KEY = 'someUserName'
APPLICATION_SECRET = 'INSERT_YOUR_APP_SECRET_HERE'

userBase = dict()

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
        if 'imagesId' not in body:
            self.write_error(400, errorCode=40001, message='image not found')
        if 'size' not in body:
            self.write_error(400, errorCode=40001, message='size not found')
        
        conf = body["confidence"]
        size = body ["size"]
        ids = body ["imagesId"]

        imgs = []
        for img in ids:
            img.append(f"images/{id}")

        result = sat_utils.detect(imgs,conf,size)

        self.write(json.dumps(result))
"""
       im = Image.fromarray(np.uint8(result.render()[0]))

        im.save("temp/tempImage.jpg")

        with open("temp/tempImage.jpg","rb") as f:
            encodedImage = base64.b64encode(f.read()) 
"""
        
class satDetectDiffHandler(RestResource):

    def post(self):
        body = json.loads(self.request.body)

        if "confidence" not in body:
            self.write_error(400, errorCode=40001, message='confidence not found')
        if 'imageId1' not in body:
            self.write_error(400, errorCode=40001, message='image 1 not found')
        if 'imageId2' not in body:
            self.write_error(400, errorCode=40001, message='image 2 not found')
        if 'size' not in body:
            self.write_error(400, errorCode=40001, message='size not found')
        
        conf = body["confidence"]
        size = body ["size"]
        id1 = body ["imageId1"]
        id2 = body ["imageId2"]

        img1 = f"images/{id1}"
        img2 = f"images/{id2}"

        result = sat_utils.detectDiff(img1,img2,conf,size)

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

backend = tornado.web.Application([
    (r"/ping", PingHandler),
    (r"/detect", satDetectHandler),
    (r"/image", satImageHandler),
    #(r"/detect-general", satDetectGeneral),
    (r"/detectDiff", satDetectDiffHandler),
    #(r"/detect-sar", satDetectSar),
    #(r"/stitch", satStitch),
])

class ExampleHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Description end-point
        ---
        tags:
        - Example
        summary: Create user
        description: This can only be done by the logged in user.
        operationId: examples.api.api.createUser
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Created user object
          required: false
          schema:
            type: object
            properties:
              id:
                type: integer
                format: int64
              username:
                type:
                  - "string"
                  - "null"
              firstName:
                type: string
              lastName:
                type: string
              email:
                type: string
              password:
                type: string
              phone:
                type: string
              userStatus:
                type: integer
                format: int32
                description: User Status
        responses:
        "201":
          description: successful operation
        """
        print("I'm the example")

class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/api/example", ExampleHandler, name="example"),
    ]
    def __init__(self):
        settings = {"debug": True}
        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":

    print ("Starting Sinch demo backend on port: \033[1m" + str(HTTP_PORT) +'\033[0m')
    print ("--- LOG ---")
    backend.listen(HTTP_PORT)
    tornado.ioloop.IOLoop.instance().start()
    #print ("Application key: \033[1m" + APPLICATION_KEY +'\033[0m')
    #print ("Post JSON object to \033[1m/register\033[0m to create user")
    #print ("Post JSON object to \033[1m/login\033[0m to retrieve authentication token")
    #print ("Example JSON: {username: 'someUserName', password: 'highlySecurePwd'}")
    tornado.options.define("port", default="9001", help="Port to listen on")
    tornado.options.parse_command_line()
    app = Application()
    app.listen(port=9001)
    tornado.ioloop.IOLoop.current().start()
    
    

  

    
