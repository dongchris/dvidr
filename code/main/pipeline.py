"""
Created on April 13, 2018

@author: D/vidr
"""

import io

from google.cloud import vision
from google.cloud.vision import types
import sys
import re

import boto
from boto.s3.key import Key

import skimage.io as skio
import cv2
import base64
from io import BytesIO
from PIL import Image
import numpy as np

# import os
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
# "/home/ec2-user/group-assignment-2-dvidr/code/main/apikey.json"


def detect_text(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    image.source.image_uri = uri

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


def simple_process(text):
    """
        This function will take the output from readImagefromS3 function as
        input and process to get receipt items and payment amounts.

    """

    text_list = text.split('\n')

    pattern = r'^\d+\s[\d|\D]+'
    result = {}
    text_list = text_list[4:]
    for index, item in enumerate(text_list):
        if re.findall(pattern, str(item)):
            result[item] = index
    num_items = len(result.keys())
    for key in result.keys():
        result[key] = "$" + str(text_list[(result[key] + num_items)])
    return result


def bounding_box(url, texts):
    """add bounding box to image, return image numpy array
    """
    img = skio.imread(url)
    for text in texts[1:]:  # 0th bounding box is whole picture
        vertices = [(vertex.x, vertex.y)
                for vertex in text.bounding_poly.vertices]   # get coordinates
        cv2.polylines(img, [np.array(vertices)], True, (0,255,0), 2)  # plot line

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
    texts = detect_text(filepath)[1]
    print(texts)
    output = simple_process(texts)
    print(output)
