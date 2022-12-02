import wandb
import os
import string
import sys
import numpy as np
import pandas as pd
import ast
import torch
import PIL
from tqdm.auto import tqdm
import shutil as sh
from pathlib import Path
import random
from IPython.display import Image, clear_output
import matplotlib.pyplot as plt
from skimage.metrics import structural_similarity
import cv2


# Main

def detect(imgs, conf, size) :
    model = torch.hub.load('ultralytics/yolov5', 'custom', 'exp2/weights/best.pt')
    model.conf = float(conf)

    results = model(imgs, size=int(size))
 
    resDicts = []

    for i in range(len(imgs)):
        resDicts.append({})
        for key, value in results.names.items():
            resDicts[i][value] = []

        for pred in results.pred[i]:
            resDicts[i][results.names[int(pred[5])]].append({'coords': pred[0:4].tolist(), 'confidence': float(pred[4])})

    return resDicts


def Appears(x, y, offset):
    for el in y:
        el_check = True
        for i in range(0, len(el)):
            if x[i] < el[i] - offset or x[i] > el[i] + offset:
                el_check = False
        if(el_check):
            return True
    
    return False

def detectDiff (im1,im2,conf,size) :

    model = torch.hub.load('ultralytics/yolov5', 'custom', 'exp2/weights/best.pt')
    model.conf = float(conf)

    results = model([im1, im2], size=int(size))

    # New objects
    new = [results.pred[1][i] for i, x in enumerate(results.pred[1][:, 0:4]) if not Appears(x, results.pred[0][:, 0:4], 20)]

    # Old objects
    old = [results.pred[0][i] for i, x in enumerate(results.pred[0][:, 0:4]) if not Appears(x, results.pred[1][:, 0:4], 20)]

    resDict = {}
    for key, value in results.names.items():
        resDict[value] = []
    annotations = []
    if(len(new)>0):
        annotations = annotations + new
    if(len(old)>0):
        annotations = annotations + old
        
    if(len(annotations)>0):
        changes = torch.stack(annotations)
        for pred in changes:
            resDict[results.names[int(pred[5])]].append({'coords': pred[0:4].tolist(), 'confidence': float(pred[4])})
    
    return resDict


def detectAllDiff (img1,img2, minArea) :

    im1 = cv2.imread(img1)
    im2 = cv2.imread(img2)
    # Convert images to grayscale
    im1_gray = cv2.cvtColor(im1, cv2.COLOR_BGR2GRAY)
    im2_gray = cv2.cvtColor(im2, cv2.COLOR_BGR2GRAY)
    # Compute SSIM between the two images
    (score, diff) = structural_similarity(im1_gray, im2_gray, full=True)
    diff = (diff * 255).astype("uint8")
    diff_box = cv2.merge([diff, diff, diff])
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    filled_im2 = im2.copy()
    rects = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > minArea:
            (x,y,w,h) = cv2.boundingRect(c) # x,y,w,h
            rects.append({'x': x, 'y': y, 'w': w, 'h': h})
    
    return rects

