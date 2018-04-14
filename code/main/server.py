from flask import Flask, render_template, Response, request, redirect, url_for
import os
from pipeline import *

app = Flask(__name__, template_folder='../templates',
            static_folder='../static')


@app.route("/")
def index():
    """Show homepage"""
    return render_template('index.html')


@app.route("/process")
def process():
    """Process text upon clicking button"""
    filepath = (readImagefromS3("85c.jpg"))
    texts = detect_text(filepath)
    output = simple_process(texts)

    items = [item for item in output.keys()]
    prices = [price for price in output.values()]
    texts = zip(items, prices)
    return render_template('index.html', texts=texts)


@app.route("/login")
def user_login():
    """Login / Register page -- not yet implemented"""
    return render_template('login.html')


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=8080)
