import base64
import datetime
from datetime import datetime
import errno
import glob
import inspect
import numpy as np
import os
import pandas as pd
import PIL
import random
import shutil
import subprocess
import sys
import threading
import tqdm
import yaml

from subprocess import check_output

def getTrainingFolder():
    i = 1
    while os.path.exists("train/training_" + str(i+1)):
        i = i+1
    
    return "train/training_" + str(i), i

def setTrainingFolder(i):
    return "train/training_" + str(i), i

def existsTraining(i):
    exists = False
    if os.path.exists("train/training_" + str(i)):
        exists = True
    
    return exists

def existsModel(i):
    exists = False
    if os.path.exists("models/model_" + str(i) + "/weights/best.pt"):
        exists = True
    
    return exists

def createTrainingFolder():
    i = 1
    while os.path.exists("train/training_" + str(i)):
        i = i+1
    
    createTrainingTree(i)

    return i

def deleteTrainingFolder(i):
    # Backup?
    shutil.rmtree("train/training_" + str(i))

def getStatus(jobId):
    result = {}
    if not existsTraining(jobId) or not os.path.isfile("logs/training_" + str(jobId) + ".log"):
        result["response"] = "jobId does not exist"
    else:
        with open("logs/training_" + str(jobId) + ".log", 'r') as file:
            logs = file.read()
        
        result["response"] = logs
    
    return result

def annotations2csv(folder, name, annotations):
    for object in annotations:
        object["image"] = name

    df = pd.DataFrame()
    if os.path.exists(folder + "/" + "annotations.pkl"):
        df = pd.read_pickle(folder + "/" + "annotations.pkl")

    df_new = pd.json_normalize(annotations)
    df_new["image_id"] = name

    # df_new.to_pickle(folder + "/" + "df_normalized.pkl")

    # df_new['bounds'] = "("+df_new['bounds.x1'].astype(int).astype(str)+","+df_new['bounds.y1'].astype(int).astype(str)+","+df_new['bounds.x2'].astype(int).astype(str)+","+df_new['bounds.y2'].astype(int).astype(str)+")"
    # df_new['bounds'] = tuple(list(df_new['bounds.x1'].astype(int).astype(str), df_new['bounds.y1'].astype(int).astype(str), df_new['bounds.x2'].astype(int).astype(str), df_new['bounds.y2'].astype(int).astype(str)))

    df_new['height'] = df_new['bounds.y2'] - df_new['bounds.y1']
    df_new['width'] = df_new['bounds.x2'] - df_new['bounds.x1']

    # df_new.drop(columns=['bounds.x1', 'bounds.x2', 'bounds.y1', 'bounds.y2'], inplace=True)
    
    df_new = df_new[['image_id','class', 'bounds.x1', 'bounds.x2', 'bounds.y1', 'bounds.y2' ,'width','height']]

    df = pd.concat([df,df_new], ignore_index=True)
    
    df = df.astype({"width": int, "height": int})

    df.to_pickle(folder + "/" + "annotations.pkl")

def addToTraining(modelId, image, objects):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
    frmt = "png"
    name = f"img_{timestamp}_1.{frmt}"

    # Write img in training_n ...
    folder = "train/training_" + str(modelId)

    with open(folder + "/images/" + name, "wb") as fh:
        fh.write(base64.b64decode(image))

    # Writes annotations in training_i/annotations.csv
    annotations2csv(folder, name, objects)

    response = {"imageId" : name}

    return response

def removeFromTraining(modelId, imageName):
    response = {}
    r_status = None
    # Remove img from training_n ...
    folder = "train/training_" + str(modelId)

    if os.path.exists(folder + "/images/" + imageName):
        os.remove(folder + "/images/" + imageName)
        response["result"] = "Success"
    else:
        response["result"] = "Image " + imageName + " does not exist in training set of model " + str(modelId)
    
    return response

def getTrainingData(incremental=True):
    folder, _ = getTrainingFolder()

    # Get list of file in folder
    files = []
    if incremental:
        files = os.listdir( + "/images/")
    
    response = {"result" : files}

    return response

def tag_is_inside_tile(class_dict, class_name, bounds, x_start, y_start, width, height, truncated_percent):
    
    x_min = bounds['x1']
    y_min = bounds['y1']
    x_max = bounds['x2']
    y_max = bounds['y2']

    x_min, y_min, x_max, y_max = x_min - x_start, y_min - y_start, x_max - x_start, y_max - y_start

    id_class = class_dict[class_name]
    
    if (x_min > width) or (x_max < 0.0) or (y_min > height) or (y_max < 0.0):
        return None
    
    x_max_trunc = min(x_max, width) 
    x_min_trunc = max(x_min, 0) 
    if (x_max_trunc - x_min_trunc) / (x_max - x_min) < truncated_percent:
        return None

    y_max_trunc = min(y_max, width) 
    y_min_trunc = max(y_min, 0) 
    if (y_max_trunc - y_min_trunc) / (y_max - y_min) < truncated_percent:
        return None
        
    x_center = (x_min_trunc + x_max_trunc) / 2.0 / width
    y_center = (y_min_trunc + y_max_trunc) / 2.0 / height
    x_extend = (x_max_trunc - x_min_trunc) / width
    y_extend = (y_max_trunc - y_min_trunc) / height
    
    return (id_class, x_center, y_center, x_extend, y_extend)

class TrainingTask(threading.Thread):
    def __init__(self, modelId, trainingData):
        super(TrainingTask, self).__init__()

        # Models to copy data from
        self.trainingData = trainingData

        # Tiles images format
        self.tiles_format = ".png"

        # Get folders
        self.training_folder, self.ith = setTrainingFolder(modelId)
        self.train_folder = self.training_folder + "/data/train/"
        self.val_folder = self.training_folder + "/data/val/"

        # Class dictionary
        self.class_dict = {}

        # Tiles size
        self.tiles_width = 0
        self.tiles_height = 0

        # Logs
        # Writing logs ith+training.log
        self.log_file = "logs/training_" + str(self.ith) + ".log"

        writeLog(self.log_file, os.getcwd())
        
    def writeConfigFile(self):
        class_list = '['
        n_classes = len(self.class_dict)
        
        for idx, class_name in enumerate(self.class_dict):

            if(idx != n_classes - 1):
                class_list = class_list + '\'' + class_name + '\','
            else:
                class_list = class_list + '\'' + class_name + '\']'

        config_file = {}
        config_file["train"] = "../" + self.train_folder
        config_file["val"] = "../" + self.val_folder
        config_file["nc"] = n_classes
        # config_file["names"] = class_list

        with open(self.training_folder + '/dataset.yml', 'w') as outfile:
            outfile.write("names: " + class_list + "\n")
            yaml.dump(config_file, outfile, default_flow_style=False)

    def copyTrainingData(self, training_sets):
        
        train_images_ith = self.train_folder + "images/"
        train_labels_ith = self.train_folder + "labels/"
        val_images_ith = self.val_folder + "images/"
        val_labels_ith = self.val_folder + "labels/"

        for i in training_sets:
            writeLog(self.log_file, "Copying training set nr " + str(i) + "...")
            
            train_images = glob.glob("train/training_" + str(i) + "/data/train/images/*" + self.tiles_format)
            train_labels = glob.glob("train/training_" + str(i) + "/data/train/labels/*.txt")
            val_images = glob.glob("train/training_" + str(i) + "/data/val/images/*" + self.tiles_format)
            val_labels = glob.glob("train/training_" + str(i) + "/data/val/labels/*.txt")

            writeLog(self.log_file, train_images_ith)
            writeLog(self.log_file, train_labels_ith)
            writeLog(self.log_file, os.path.abspath(train_images_ith))
            writeLog(self.log_file, train_images)
            writeLog(self.log_file, train_labels)
            writeLog(self.log_file, val_images)
            writeLog(self.log_file, val_labels)
            
            for image_path in train_images:
                forceSymlink(os.path.abspath(image_path), os.path.abspath(train_images_ith) + "/" + str(i) + "_" + image_path.split('/')[-1])

            for label_path in train_labels:
                forceSymlink(os.path.abspath(label_path), os.path.abspath(train_labels_ith) + "/" + str(i) + "_" + label_path.split('/')[-1])

            for image_path in val_images:
                forceSymlink(os.path.abspath(image_path), os.path.abspath(val_images_ith)+ "/" + str(i) + "_" + image_path.split('/')[-1])

            for label_path in val_labels:
                forceSymlink(os.path.abspath(label_path), os.path.abspath(val_labels_ith) + "/" + str(i) + "_" + label_path.split('/')[-1])
   

    def getTrainingList(self, training_idx):
        """
        Copy list of images of the previous training sets
        """
        imgList = []
        imgList += glob.glob("train/training_" + str(training_idx) + "/images/*.png")
        imgList += glob.glob("train/training_" + str(training_idx) + "/images/*.jpg")

        writeLog(self.log_file, "Annotating and tiling the following images: ")
        writeLog(self.log_file, imgList)

        return imgList

    def createTiles(self, imgList, tiles_dir, labels_dir, img_height, img_width, tiles_width, tiles_height, overlap, truncated_perc = 0.3, overwrite = True):

        # Opening annotations
        annotations_df = pd.read_pickle(self.training_folder + "/annotations.pkl")

        # Generating dictionary of class_names -> ids
        class_list = sorted(annotations_df["class"].unique())

        writeLog(self.log_file, annotations_df["class"].value_counts())
        
        for id, class_name in enumerate(class_list):
            self.class_dict[class_name] = id

        # Random seed for train/val split
        random.seed(2)

        for img_path in tqdm.tqdm(imgList): # For image

            pil_img = PIL.Image.open(img_path, mode='r')
            np_img = np.array(pil_img, dtype=np.uint8)

            img_labels = annotations_df[annotations_df["image_id"] == os.path.basename(img_path)]

            x_tiles = (img_width + tiles_width + overlap - 1) // tiles_width 
            y_tiles = (img_height + tiles_height + overlap - 1) // tiles_height

            # Cut each tile
            for x in range(x_tiles):
                for y in range(y_tiles):
                    
                    x_end = min((x + 1) * tiles_width - overlap * (x != 0), img_width)
                    x_start = x_end - tiles_width
                    y_end = min((y + 1) * tiles_height - overlap * (y != 0), img_height)
                    y_start = y_end - tiles_height
                    #print(x_start, y_start)

                    # 20% of tiles in val, 80% in train
                    rand = random.randint(1, 100) 
                    folder = 'val' if rand<=20 else 'train'
                    #save_tile_path = tiles_dir[folder].joinpath(img_path.stem + "_" + str(x_start) + "_" + str(y_start) + self.tiles_format)
                    save_tile_path = tiles_dir[folder] + os.path.splitext(os.path.basename(img_path))[0] + "_" + str(x_start) + "_" + str(y_start) + self.tiles_format

                    #save_label_path = labels_dir[folder].joinpath(img_path.stem + "_" + str(x_start) + "_" + str(y_start) + ".txt")
                    save_label_path = labels_dir[folder] + os.path.splitext(os.path.basename(img_path))[0] + "_" + str(x_start) + "_" + str(y_start) + ".txt"

                    # Save if file doesn't exit
                    if overwrite or not os.path.isfile(save_tile_path):
                        cut_tile = np.zeros(shape=(tiles_width, tiles_height, 3), dtype=np.uint8)
                        cut_tile[0:tiles_height, 0:tiles_width, :] = np_img[y_start:y_end, x_start:x_end, :]
                        cut_tile_img = PIL.Image.fromarray(cut_tile)
                        cut_tile_img.save(save_tile_path)

                    found_tags = []

                    for index, row in img_labels.iterrows():
                        bounds = {}
                        bounds['x1'] = row['bounds.x1']
                        bounds['x2'] = row['bounds.x2']
                        bounds['y1'] = row['bounds.y1']
                        bounds['y2'] = row['bounds.y2']
                        
                        tags = tag_is_inside_tile(self.class_dict, row['class'], bounds, x_start, y_start, tiles_width, tiles_height, truncated_perc)

                        if tags is not None:
                            found_tags.append(tags)

                    # writeLog(self.log_file, img_labels['bounds'].apply(tuple, axis=1))
                    # found_tags = [ tag_is_inside_tile(self.class_dict, img_labels['class'].iloc[i], bounds, x_start, y_start, tiles_width, tiles_height, truncated_perc) for i, bounds in enumerate(img_labels['bounds'])]
                    
                    #The following print tracks how the function creates each image tile and .txt with the tags

                    #e mpty_tags = [el for el in found_tags if el is None]
                    # print(len(empty_tags))

                    # found_tags = [el for el in found_tags if el is not None]

                    # save labels
                    with open(save_label_path, 'w+') as f:
                        for tags in found_tags:
                            f.write(' '.join(str(x) for x in tags) + '\n')

        return True

    def train(self):
        params = {}
        params["tile_size"] = 512 # max(self.tiles_width, self.tiles_height)
        params["batch"] = 16
        params["epochs"] = 10
        params["config_file"] = self.training_folder + '/dataset.yml'
        params["model"] = "./yolov5s.pt"
        params["output_dir"] = "../../../models/model_" + str(self.ith)

        writeLog(self.log_file, "Params:")
        writeLog(self.log_file, params)
        param_img = "--imgsz"
        param_batch = "--batch-size"
        param_epochs = "--epochs"
        param_data = "--data"
        param_weights = "--weights"
        param_name = "--name"
        
        # Removing existing model_i directory
        shutil.rmtree("models/model_" + str(self.ith))

        script_path = os.path.join(get_script_dir(), 'yolov5/train.py')
        
        with open(self.log_file, "a") as f:
            subprocess.Popen([sys.executable, 
                                script_path, 
                                param_img, 
                                str(params["tile_size"]),
                                param_batch,
                                str(params["batch"]),
                                param_epochs,
                                str(params["epochs"]),
                                param_data,
                                params["config_file"],
                                param_weights,
                                params["model"],
                                param_name,
                                params["output_dir"]
                                ], stdout=f, stderr=f)

    def run(self):

        # Make new directory for next training data
        # writeLog(self.log_file, "Creating new training folder")
        # createTrainingFolder()

        # Get image list of training data
        writeLog(self.log_file, "Fetching new images")
        imgList = self.getTrainingList(self.ith)
        
        # Create tiles
        writeLog(self.log_file, "Starting tiles creation...")
        
        # Tiles params
        pick_first = imgList[0] # Picking first image
        img = PIL.Image.open(pick_first) # Opening it
        img_height, img_width = img.size # Getting image size
        self.tiles_width = img_width // 5
        self.tiles_height = img_height // 5
        
        tiles_overlap = max(img_height, img_width) // 40

        tiles_dir = {}
        tiles_dir["train"] = self.train_folder + "images/"
        tiles_dir["val"] = self.val_folder + "images/"
        labels_dir = {}
        labels_dir["train"] = self.train_folder + "labels/"
        labels_dir["val"] = self.val_folder + "labels/"
        
        self.createTiles(
            imgList = imgList, 
            tiles_dir=tiles_dir, 
            labels_dir=labels_dir,
            img_height = img_height,
            img_width = img_width,
            tiles_width = self.tiles_width,
            tiles_height = self.tiles_height,
            overlap = tiles_overlap
            )

        writeLog(self.log_file, "Tiles created")

        # Copying data form previous training sets
        writeLog(self.log_file, "Copying training data...")
        trainings_to_copy = self.trainingData
        
        self.copyTrainingData(trainings_to_copy)

        writeLog(self.log_file, "Writing config file...")
        self.writeConfigFile()
        
        writeLog(self.log_file, "Running training...")
        self.train()

def trainModel(modelId, trainingData = None):
    response = {}

    # If there are training data, run the model training
    if len(glob.glob("train/training_" + str(modelId) + "/images/*.png")) == 0 and len(glob.glob("train/training_" + str(modelId) + "/images/*.jpg")) == 0:
        response["result"] = "Not enough training data for model " + str(modelId)
    
    for training in trainingData:
        if modelId == training:
            response["result"] = "Data of model " + str(modelId) + " has already been used for the training"
        if not existsTraining(training):
            response["result"] = "No data to fetch for model " + str(modelId)

    if "result" not in trainingData:
        training = TrainingTask(modelId, trainingData)
        training.start()
        response["jobId"] = modelId
        

    return response

def createModel():
    response = {}
    ith = createTrainingFolder()

    createTrainingTree(ith)
    response["modelId"] = ith

    return response

def deleteModel(modelId):
    response = {}

    try:
        deleteTrainingFolder(modelId)
        response["response"] = "OK"
    except OSError as e:
        print(e.errno)
        response["response"] = "No model number " + str(modelId)

    return response

def getModels():
    response = {}
    # Get list of file in folder
    files = os.listdir("models") # to be completed with all info (date, ID)

    response["models"] = files
    
    return response

def getClasses(modelId):
    response = {}
    # Get list of file in folder
    # Opening annotations
    path = "train/training_" + str(modelId) + "/annotations.pkl"

    if os.path.exists("train/training_" + str(modelId)):
        annotations_df = pd.read_pickle(path)
        # Generating dictionary of class_names -> ids
        class_list = sorted(annotations_df["class"].unique())

        response["classes"] = class_list

    return response
    
def writeLog(path, obj):
    date_time = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    with open(path, "a") as logfile:
        logfile.write(date_time + ":" + str(obj) + "\n")

def createTrainingTree(ith):
    if not os.path.exists("train/training_" + str(ith)):
        os.makedirs("train/training_" + str(ith))
        os.makedirs("train/training_" + str(ith) + "/images")
        os.makedirs("train/training_" + str(ith) + "/data")
        os.makedirs("train/training_" + str(ith) + "/data/train")
        os.makedirs("train/training_" + str(ith) + "/data/train/images")
        os.makedirs("train/training_" + str(ith) + "/data/train/labels")
        os.makedirs("train/training_" + str(ith) + "/data/val")
        os.makedirs("train/training_" + str(ith) + "/data/val/images")
        os.makedirs("train/training_" + str(ith) + "/data/val/labels")

    if not os.path.exists("models/model_" + str(ith)):
        os.makedirs("models/model_" + str(ith))

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def forceSymlink(file1, file2):
    try:
        os.symlink(file1, file2)
    except OSError as e:
        if e.errno == errno.EEXIST:
            os.remove(file2)
            os.symlink(file1, file2)