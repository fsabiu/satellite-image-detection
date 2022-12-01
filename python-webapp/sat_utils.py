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


# Main

def detect(img, conf, size) :

    model = torch.hub.load('ultralytics/yolov5', 'custom', 'exp2/weights/best.pt')
    model.conf = float(conf)

    im1 = img

    results = model(im1, size=int(size))

    resDict = {}
    for key, value in results.names.items():
        resDict[value] = []
        
    for pred in results.pred[0]:
        resDict[results.names[int(pred[5])]].append({'coords': pred[0:4].tolist(), 'confidence': float(pred[4])})

    return resDict


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