from image_clustering.src.utils.config import get_config_from_json
from image_clustering.src.models.feature_extractor import run_inference_on_images_feature
import os


def extract_feature(img_dir, model_dir, output_dir):
    """
    Extract image features of all images in img_dir and save feature vectors to output_dir
    :param img_dir: (string) directory containing images to extract feature
    :param model_dir: (string) directory containing extractor model
    :param output_dir: (string) directory to save feature vector file
    :return:
    """
    # Get list of image paths
    img_list = [os.path.join(img_dir, img_file) for img_file in os.listdir(img_dir) if img_file.endswith('jpg')]

    # Run getting feature vectors for each image
    run_inference_on_images_feature(img_list, model_dir, output_dir)


def cluster_data():

    # Extracting features
    extract_feature('train/training_0/data/train/images', 'image_clustering/src/models', 'image_clustering/results/vectors')
