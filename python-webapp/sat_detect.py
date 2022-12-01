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

    return results
    # Results save
    #results.save(save_dir=str(sys.argv[2]))

""" if __name__ == "__main__":
    
    if(len(sys.argv) < 5):
        print("Invalid parameters.")
        print("Usage: python " + sys.argv[0] + " path/img.jpg path/output/ conf img_size")
        exit(1)

    if(float(sys.argv[3])< 0 or float(sys.argv[3])>1):
        print("Invalid conf parameter. Must be between 0 and 1.")
        exit(1)
    
    if(int(sys.argv[4])< 0):
          print("Invalid img_size parameter. Must be greater than 0")
          exit(1)

    model = torch.hub.load('./yolov5', 'custom', '/home/oracle/satellite-imgs/exp2/weights/best.pt', source= 'local')
    model.conf = float(sys.argv[3])

    im1 = sys.argv[1]

    results = model(im1, size=int(sys.argv[4]))

    # Results save
    results.save(save_dir=str(sys.argv[2]))
 """