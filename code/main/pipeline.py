"""
Created on April 13, 2018

@author: D/vidr
"""


from boto.s3.key import Key
from google.cloud import vision
from google.cloud.vision import types
from io import BytesIO
from PIL import Image
import skimage.io as skio

import base64
import boto
import cv2
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")
import io
import numpy as np
import re
import sys

from text_processingv3 import simple_process

# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \


# def detect_text(uri):
#     """Detects text in the file located in
#        Google Cloud Storage or on the Web.
#     """
#     client = vision.ImageAnnotatorClient()
#     image = types.Image()
#     image.source.image_uri = uri
#
#     response = client.text_detection(image=image)
#     texts = response.text_annotations
#
#     return (texts, texts[0].description.encode('ascii',
#                                                'ignore').decode('ascii'))


def download_img(img_url):
    """Download image from url.
    """
    img = skio.imread(img_url)
    return img


def detect_text(path):
    """Detects text in the file from local"""
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    return (texts, texts[0].description.encode('ascii',
                                               'ignore').decode('ascii'))


def readImagefromS3(imageFile):
    """
        This function will be using the pem file for AWS.
        It will access a public S3 bucket called dvidr with
        the specified image file. The output is a url link
        for the image that will be passed onto the Google
        Cloud Vision API for processing.
    """
    with open('../../../dvidr.pem') as f:
        keys = f.read().split(',')

    s3 = boto.connect_s3(
        aws_access_key_id=keys[0],
        aws_secret_access_key=keys[1]
    )
    bucket = s3.get_bucket("dvidr", validate=False)

    k1 = Key(bucket)
    k1.key = imageFile

    url_name = k1.generate_url(259200)
    return url_name


# def bounding_box(url, texts):
#     """add bounding box to image, return image numpy array
#     """
#     img = skio.imread(url)
#     for text in texts[1:]:  # 0th bounding box is whole picture
#         vertices = [(vertex.x, vertex.y)  # get coordinates
#                     for vertex in text.bounding_poly.vertices]
#         cv2.polylines(img, [np.array(vertices)],
#                       True, (0, 255, 0), 2)  # plot line
#
#     return img


def bounding_box(img_path, texts):
    """add bounding box to straightened image, return image numpy array
    """
    # read image from local
    img = plt.imread(img_path)

    # convert gray-scale to RGB
    if len(img.shape) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)

    for text in texts[1:]:  # 0th bounding box is whole picture
        vertices = [(vertex.x, vertex.y)  # get coordinates
                    for vertex in text.bounding_poly.vertices]
        cv2.polylines(img, [np.array(vertices)],
                      True, (0, 255, 0), 2)  # plot line

    return img


def arr2str(img_arr):
    """convert a image from numpy array to base64 output
    """
    pil_img = Image.fromarray(img_arr)
    buff = BytesIO()
    pil_img.save(buff, format="JPEG")
    new_image_string = base64.b64encode(buff.getvalue()).decode("utf-8")
    new_image_string = "data:image/jpg;base64," + new_image_string
    return new_image_string


if __name__ == '__main__':
    filepath = (readImagefromS3("85c.jpg"))
    texts = detect_text(filepath)[0]
    print(texts)
    output = simple_process(texts)
    print(output)
