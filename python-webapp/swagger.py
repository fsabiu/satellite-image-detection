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
          description: Detection of objects within the given image using the given model.
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
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

class addToTrainingSet(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect object(s)
        description: Add image to the training set of the given model
        operationId: sat.api.addToTrain
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          description: Detection of objects within the given image using the given model.
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
              imageData:
                type: string
                required: true
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
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  response:
                    type: string
        """

class removeFromTrainingSet(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect object(s)
        description: Remove image from the training set of the given model
        operationId: sat.api.remFromTrain
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
              imageId:
                type: string
                required: true
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  response:
                    type: string
        """

class createModel(tornado.web.RequestHandler):
    def get(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect object(s)
        description: Create a new prediction model identified by the returned id
        operationId: sat.api.createModel
        produces:
        - application/json
        parameters:
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  modelId:
                    type: string
        """

class deleteModel(tornado.web.RequestHandler):
    def delete(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Detect object(s)
        description: Delete a prediction model identified by the given id (except for model 0, that is the base model)
        operationId: sat.api.deleteModel
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  modelId:
                    type: string
        """

class getStatus(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Get jobId status
        description: Get the log file of the job with the specified jobId
        operationId: sat.api.getStatus
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              jobId:
                type: number
                format: int
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  response:
                    type: string
        """

class getModels(tornado.web.RequestHandler):
    def get(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Get prediction models
        description: Get a list of the model names and ids.
        operationId: sat.api.getModels
        produces:
        - application/json
        parameters:
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  models:
                    type: array
                    items:
                      properties:
                        id:
                          type: number
                          format: int
                        name:
                          type: string
        """

class getClasses(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Get classes of a specified model
        description: Get the class list of the model with the given modelId
        operationId: sat.api.getClasses
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  classes:
                    type: array
                    items:
                      type: string
        """

class trainModel(tornado.web.RequestHandler):
    def post(self):
        """
        Description end-point
        ---
        tags:
        - Satellite images
        summary: Train the specified model
        description: Train the model having the specified modelId including labelled data from other models
        operationId: sat.api.trainModel
        produces:
        - application/json
        parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              modelId:
                type: number
                format: int
              trainingData:
                type: array
                items:
                  type: number
                  format: int
        responses:
          200:
              description: Successful
              schema:
                type: object
                properties:
                  jobId:
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
        tornado.web.url(r"/addToTrainingSet", addToTrainingSet, name="Add image to training set"),
        tornado.web.url(r"/removeFromTrainingSet", removeFromTrainingSet, name="Remove image from training set"),
        tornado.web.url(r"/createModel", createModel, name="Create a new prediction model"),
        tornado.web.url(r"/deleteModel", deleteModel, name="Delete a prediction model with its training and validation sets"),
        tornado.web.url(r"/getStatus", getStatus, name="Get the status of the job with the specified jobId"),
        tornado.web.url(r"/getModels", getModels, name="Get the list of trained prediction models"),
        tornado.web.url(r"/getClasses", getClasses, name="Get the list of the classes of the specified model"),
        tornado.web.url(r"/trainModel", trainModel, name="Train a model and get the id of the job"),

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
    
    

  

    
