from flask import Flask, render_template, Response, request, redirect, url_for
import os
from pipeline import *
from text_processingv2 import simple_process

filename = None
app = Flask(__name__, template_folder='../templates',
            static_folder='../static')


@app.route("/")
def index():
    """Show homepage"""
    return render_template('index.html')


@app.route("/uploader", methods=['POST', 'GET'])
def get_filename():
    print(request)
    global filename
    if request.method == 'POST':
        filename = request.form['filename']
        print('upload ', filename)
        return render_template('index.html')
    else:
        return render_template('index.html')


@app.route("/process")
def process():
    """
    Process text upon clicking button;
    Add bounding box to image
    """
    # OCR
    filepath = (readImagefromS3(filename))
    texts = detect_text(filepath)

    # add bounding box
    img_arr = bounding_box(filepath, texts[0])
    img_str = arr2str(img_arr)
    print(img_str[:30] + "..." + img_str[-20:])

    # process text
    output = simple_process(texts[1], n=5)
    global items
    items = [item for item in output.keys()]
    prices = [price for price in output.values()]
    global prices2
    prices2 = [float(price[1:]) for price in prices]
    prices2 = [prices2[i] * -1 if items[i].lower() == 'discount'
               else prices2[i] for i in range(len(prices2))]
    texts = zip(items, prices)
    return render_template('index.html', texts=texts, img_str=img_str)


@app.route("/login")
def user_login():
    """Login / Register page -- not yet implemented"""
    return render_template('login.html')


@app.route('/split', methods=['GET', 'POST'])
def split():
    if request.method == "POST":
        payer_list = request.form.getlist("payers", None)
        import numpy as np
        if payer_list is not None:
            d = dict()
            for i in range(len(items)):
                if payer_list[i] in d:
                    d[payer_list[i]].append(prices2[i])
                else:
                    d[payer_list[i]] = [prices2[i]]
            payer = []
            totalprice = []
            for key, val in d.items():
                payer.append(key)
                totalprice.append('%.2f' % np.sum(val))
            combine = zip(payer, totalprice)

            return render_template("index.html",
                                   payer_list=payer_list, combine=combine)
    return render_template("index.html")


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
