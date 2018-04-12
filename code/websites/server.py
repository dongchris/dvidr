from flask import Flask, render_template

import io
import numpy as np
from google.cloud import vision
from google.cloud.vision import types
import sys
import re

app = Flask(__name__)

def detect_text(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations

    output = []
    for text in texts:
        output.append('"{}"'.format(text.description))
    return "\n".join(output)

import boto
from boto.s3.key import Key

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

filepath = (readImagefromS3("85c.jpg"))

texts = detect_text(filepath)

def simple_process(text):
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

print(simple_process(texts))

@app.route("/")
def homepage():
    """Show homepage"""
    return render_template('index.html')

@app.route("/login")
def user_login():
    """Login / Register page -- not yet implemented"""
    return render_template('login.html')

if __name__ == '__main__':
    app.debug = True
    app.run(host = '0.0.0.0',port = 80)