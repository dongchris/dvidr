from flask import Flask, render_template, Response, request, redirect, url_for
import os
from pipeline import *

app = Flask(__name__, template_folder='../templates',
            static_folder='../static')


@app.route("/")
def index():
    """Show homepage"""
    return render_template('index.html')


filepath = (readImagefromS3("85c.jpg"))
texts = detect_text(filepath)
output = simple_process(texts)

items = [item for item in output.keys()]
prices = [price for price in output.values()]
texts = zip(items, prices)
prices2 = [float(price[1:]) for price in prices]


@app.route("/process")
def process():
    """Process text upon clicking button"""

    return render_template('index.html', texts=texts)


@app.route("/login")
def user_login():
    """Login / Register page -- not yet implemented"""
    return render_template('login.html')


@app.route('/split', methods=['GET', 'POST'])
def split():
    
    if request.method == "POST":
        payer_list = request.form.getlist("payers", None)
        import numpy as np
        if payer_list!=None:
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

            return render_template("index.html", payer_list = payer_list, combine = combine)
    return render_template("index.html")



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
