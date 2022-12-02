#!/usr/bin/env python
"""
Licensed under the MIT Licence, Copyright (c) 2014 Sinch AB

This demonstrates a basic partner backend for generating authentication tokens. 
In this example the user database is not persistent: Only for demonstrational purpose!
See rows ~100-120 for code on generating a Sinch compatible authentication token.
"""

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.web
from tornado_swagger.setup import setup_swagger

class ImageHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Upload image
        description: This function is called to upload one images.
        operationId: sat.api.image
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of objects within the image with the specified id.
          required: false
          schema:
            type: object
            properties:
              imageId:
                type: string
              confidence:
                type: number
                format: float
              size:
                type: number
                format: int
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    imageId:
                      type: string
        """

class DetectHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect object(s)
        description: This can only be called after uploading one or more images (/images).
        operationId: sat.api.detect
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of objects within the image with the specified id.
          required: false
          schema:
            type: object
            properties:
              imageId:
                type: string
              confidence:
                type: number
                format: float
              size:
                type: number
                format: int
        responses:
        "200":
          description: successful operation
        """



class Application(tornado.web.Application):
    _routes = [
        tornado.web.url(r"/image", ImageHandler, name="Image"),
        tornado.web.url(r"/detect", DetectHandler, name="Detect"),
    ]
    def __init__(self):
        settings = {"debug": True}
        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":


    tornado.options.define("port", default="9001", help="Port to listen on")
    tornado.options.parse_command_line()
    
    app = Application()
    app.listen(port=9001)
    tornado.ioloop.IOLoop.current().start()
    
    

  

    
