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
        description: Image must be encoded in base64 format
        operationId: sat.api.detect
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of objects within the given image.
          required: true
          schema:
            type: object
            properties:
              imageData:
                type: string
                required: true
              confidence:
                type: number
                format: float
              size:
                type: number
                format: int
              format:
                type: string
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    objects:
                      type: array
                      items:
                        properties:
                          class:
                            type: string
                          confidence:
                            type: number
                            format: float
                          bounds:
                            type: object
                            properties:
                              x1:
                                type: number
                                format: float
                              y1:
                                type: number
                                format: float
                              x2:
                                type: number
                                format: float
                              y2:
                                type: number
                                format: float
                        
        """

class DetectDiffHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect differences of objects between images
        description: Images must be encoded in base64 format
        operationId: sat.api.detectDiff
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of differences among objects within the given images.
          required: true
          schema:
            type: object
            properties:
              image1:
                type: string
                required: true
              image2:
                type: string
                required: true
              confidence:
                type: number
                format: float
              size:
                type: number
                format: int
              format:
                type: string
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    objects:
                      type: array
                      items:
                        properties:
                          class:
                            type: string
                          confidence:
                            type: number
                            format: float
                          bounds:
                            type: object
                            properties:
                              x1:
                                type: number
                                format: float
                              y1:
                                type: number
                                format: float
                              x2:
                                type: number
                                format: float
                              y2:
                                type: number
                                format: float
                        
        """

class DetectAllDiffHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect general differences between images
        description: Images must be encoded in base64 format
        operationId: sat.api.detectAllDiff
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of differences within the given images.
          required: true
          schema:
            type: object
            properties:
              image1:
                type: string
                required: true
              image2:
                type: string
                required: true
              minArea:
                type: number
                format: integer
              
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    objects:
                      type: array
                      items:
                        properties:
                          bounds:
                            type: object
                            properties:
                              x1:
                                type: number
                                format: float
                              y1:
                                type: number
                                format: float
                              x2:
                                type: number
                                format: float
                              y2:
                                type: number
                                format: float
                        
        """

class StitchHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Stitch two images
        description: Images must be encoded in base64 format
        operationId: sat.api.stitch
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Stitch of given images.
          required: true
          schema:
            type: object
            properties:
              image1:
                type: string
                required: true
              image2:
                type: string
                required: true
              
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    result:
                      type: string          
        """

class DetectSarDiffHandler(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect differences in SAR images
        description: SAR images must be encoded in base64 format
        operationId: sat.api.detectSAR
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of differences between the given SAR images.
          required: true
          schema:
            type: object
            properties:
              image1:
                type: string
                required: true
              image2:
                type: string
                required: true
              
        responses:
            200:
                description: Successful
                schema:
                  type: object
                  properties:
                    result:
                      type: string          
        """

class Application(tornado.web.Application):
    _routes = [
        #tornado.web.url(r"/image", ImageHandler, name="Image"),
        tornado.web.url(r"/detect", DetectHandler, name="Detect"),
        tornado.web.url(r"/detectDiff", DetectDiffHandler, name="Detect object differences"),
        tornado.web.url(r"/detectAllDiff", DetectAllDiffHandler, name="Detect general differences"),
        tornado.web.url(r"/stitch", StitchHandler, name="Stitch two images"),
        tornado.web.url(r"/detectSarDiff", DetectSarDiffHandler, name="Detect SAR differences"),

    ]
    def __init__(self):
        settings = {"debug": True}
        setup_swagger(self._routes)
        super(Application, self).__init__(self._routes, **settings)


if __name__ == "__main__":


    tornado.options.define("port", default="9001", help="Port to listen on")
    tornado.options.parse_command_line()
    
    app = Application()
    app.listen(port=3001)
    tornado.ioloop.IOLoop.current().start()
    
    

  

    
