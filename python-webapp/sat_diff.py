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
 
""" # Main
if __name__ == "__main__":
    
    if(len(sys.argv) < 6):
        print("Invalid parameters.")
        print("Usage: python " + sys.argv[0] + " path/img1.jpg path/img2.jpg path/output/ conf img_size")
        exit(1)

    if(float(sys.argv[4])< 0 or float(sys.argv[4])>1):
        print("Invalid conf parameter. Must be between 0 and 1.")
        exit(1)
    
    if(int(sys.argv[5])< 0):
          print("Invalid img_size parameter. Must be greater than 0")
          exit(1)

    print(sys.argv[1])
    print(sys.argv[2])

    model = torch.hub.load('./yolov5', 'custom', '/home/oracle/satellite-imgs/exp2/weights/best.pt', source= 'local')
    model.conf = float(sys.argv[4])

    im1 = sys.argv[1]
    im2 = sys.argv[2]

    results = model([im1, im2], size=int(sys.argv[5]))

    # New objects
    new = [results.pred[1][i] for i, x in enumerate(results.pred[1][:, 0:4]) if not Appears(x, results.pred[0][:, 0:4], 20)]

    # Old objects
    old = [results.pred[0][i] for i, x in enumerate(results.pred[0][:, 0:4]) if not Appears(x, results.pred[1][:, 0:4], 20)]

    annotations = []
    if(len(new)>0):
        annotations = annotations + new
    if(len(old)>0):
        annotations = annotations + old
    if(len(annotations)>0):
        results.pred[1] = torch.stack(annotations)

    # Checks if new or old != []
    #results.pred[1] = torch.cat([new_items, old_items])

    # Results save
    results.save(save_dir=str(sys.argv[3]))
 """