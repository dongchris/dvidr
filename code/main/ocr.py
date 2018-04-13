# import library
import numpy as np
import matplotlib.pyplot as plt
import io
import cv2
import re

# Imports the Google Cloud client library
from google.cloud import vision
from google.cloud.vision import types


def detect_text_uri(uri):
    """Detects text in the file located in Google Cloud Storage or on the Web.
    """
    client = vision.ImageAnnotatorClient()
    image = types.Image()
    image.source.image_uri = uri

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print('Texts:')

    for text in texts:
        print('\n"{}"'.format(text.description))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])

        print('bounds: {}'.format(','.join(vertices)))

    return texts


def bounding_box(url, texts):
    """
    add bounding box
    """
    img = io.imread(url)    # read image from url
    for text in texts[1:]:  # 0th bounding box is whole picture
        vertices = [(vertex.x, vertex.y) for vertex in
                    text.bounding_poly.vertices]   # get coordinates
        # plot line
        cv2.polylines(img, [np.array(vertices)], True, (0, 255, 0), 2)

    plt.figure(figsize=(10, 10))
    plt.imshow(img)
    plt.show()


def simple_process(text):
    text_list = text.split('\n')

    pattern = r'^\d+\s[\d|\D]+'
    result = {}
    for index, item in enumerate(text_list):
        if re.findall(pattern, str(item)):
            result[item] = index
    num_items = len(result.keys())
    for key in result.keys():
        result[key] = "$" + str(text_list[(result[key] + num_items)])
    return result


if __name__ == '__main__':
    url = 'https://dvidr.s3.amazonaws.com/85c.jpg?Signature=TNQbX0nd'\
            'lcmvo4d2g%2F3FXbPonwE%3D&Expires=1523662875&AWSAccessKey'\
            'Id=AKIAJ4FD4JXF5A7AKGGA'
    texts = detect_text_uri(url)
    bounding_box(url, texts)
    print(simple_process(texts))
