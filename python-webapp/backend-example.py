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

        im = Image.fromarray(np.uint8(result.render()[0]))

        im.save("temp/tempImage.jpg")

        with open("temp/tempImage.jpg","rb") as f:
            encodedImage = base64.b64encode(f.read())

        self.write(json.dumps({"result" : encodedImage.decode('ascii') }))


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
    #(r"/detect-diff", satDetectDiff),
    #(r"/detect-sar", satDetectSar),
    #(r"/stitch", satStitch),
])

if __name__ == "__main__":

    print ("Starting Sinch demo backend on port: \033[1m" + str(HTTP_PORT) +'\033[0m')
    #print ("Application key: \033[1m" + APPLICATION_KEY +'\033[0m')
    #print ("Post JSON object to \033[1m/register\033[0m to create user")
    #print ("Post JSON object to \033[1m/login\033[0m to retrieve authentication token")
    #print ("Example JSON: {username: 'someUserName', password: 'highlySecurePwd'}")
    print ("--- LOG ---")

    backend.listen(HTTP_PORT)
    tornado.ioloop.IOLoop.instance().start()
