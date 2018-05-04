from flask import Flask, render_template, Response, request, redirect, url_for
from flask_login import (current_user, LoginManager, login_required,
                         login_user, logout_user, UserMixin)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import numpy as np
import os
import cv2
from pipeline import *
from text_processingv3 import simple_process
from straighten_final import straighten

filename = None
app = Flask(__name__, template_folder='../templates',
            static_folder='../static')
db_pwd = open('db_login_info.txt', 'r').read().splitlines()
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://%s:%s@dvidrdbinstance.\
cjdc2sny2qtf.us-west-2.rds.amazonaws.com:5432/dvidrdb' % (db_pwd[0], db_pwd[1])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)
login_manager = LoginManager()


class Users(db.Model, UserMixin):
    id = db.Column(db.String(150), primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    pay_info = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def __init__(self, username, email, pay_info, password):
        self.id = hash(email)
        self.username = username
        self.email = email
        self.pay_info = pay_info
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@app.route("/")
def index():
    """Show homepage"""
    return render_template('index.html')


@app.route("/uploader", methods=['POST', 'GET'])
def get_filename():
    """Retrieve file name after uploading image"""
    print(request)
    global filename
    if request.method == 'POST':
        filename = request.form['filename']
        print('upload ', filename)
        is_uploaded = True
        return render_template('index.html', is_uploaded=is_uploaded)
    else:
        return render_template('index.html')


@app.route("/process")
def process():
    """
    Process text upon clicking button;
    Add bounding box to image
    """
    # Get image URL
    img_url = (readImagefromS3(filename))

    # (Straighten) image and save to local
    try:
        img = straighten(img_url)  # straightened
        img_path = 'tmp/tmp.jpg'
        cv2.imwrite(img_path, img)

        # OCR on straightened image
        texts = detect_text(img_path)
        output = simple_process(texts[0])  # process text
        assert output, 'empty dictionary'

    except:
        img = download_img(img_url)  # original
        img_path = 'tmp/tmp.jpg'
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) # for use of opencv
        cv2.imwrite(img_path, img)

        # OCR on straightened image
        texts = detect_text(img_path)
        output = simple_process(texts[0])  # process text

    # add bounding box
    img_arr = bounding_box(img_path, texts[0])
    img_str = arr2str(img_arr)
    print(img_str[:30] + "..." + img_str[-20:])

    # process text
    # output = simple_process(texts[0])
    print(output)
    global items
    items = [item for item in output.keys()]
    prices = [price for price in output.values()]
    global prices2
    prices2 = [float(price[1:]) if price[0] == '$' else
               float(price) for price in prices]
    prices2 = [prices2[i] * -1 if items[i].lower() == 'discount'
               else prices2[i] for i in range(len(prices2))]
    paylist = ['payer' + str(x) for x in range(len(items))]
    texts = list(zip(items, prices, paylist))

    return render_template('index.html', texts=texts, img_str=img_str)


@app.route("/login")
def user_login():
    """Display login page"""
    return render_template('login.html')


@app.route("/login", methods=['POST'])
def user_login_post():
    """Process the login request"""
    print(request.form)
    username = request.form['username']
    password = request.form['password']
    user = Users.query.filter_by(username=username).first()

    # Login and validate the user.
    if user is not None and user.check_password(password):
        login_user(user)
        # return redirect(url_for('secret_page'))
        return '<h1> Logged in : ' + username + '</h1>'
    else:
        return '<h1> Invalid username and password combination! </h1>'


@app.route('/register')
def register():
    """Display the register page"""
    return render_template('register.html')


@app.route('/register', methods=['POST'])
def register_post():
    """Process the register request"""
    username = request.form['username']
    password = request.form['password']
    email_id = request.form['email id']
    venmo_url = request.form['venmo url']

    user_count = Users.query.filter_by(username=username).count()
    if (user_count > 0):
        return "<h1> Error - Existing user : " + username + '</h1>'

    user = Users(username, email_id, venmo_url, password)
    db.session.add(user)
    db.session.commit()
    return '<h1> Registered : ' + username + '</h1>'


@app.route('/split', methods=['GET', 'POST'])
def split():
    """
    After identifying the payers responsible for each item, this
    function will allocate the prices for each payer. It will then
    print out the final prices for each user.
    """
    if request.method == "POST":
        payer_list = [request.form.getlist("payer%s" % i, None)
                      for i in range(len(items))]
        tip_amount = float(request.form.getlist("tipamount")[0]
                                       .encode('ascii'))

        print(payer_list)

        if payer_list is not None:
            d = dict()
            for i in range(len(items)):
                for j in range(len(payer_list[i])):
                    if payer_list[i][j] in d:
                        d[payer_list[i][j]].append(
                            prices2[i] / len(payer_list[i]))
                    else:
                        d[payer_list[i][j]] = [prices2[i] / len(payer_list[i])]
            global payer
            global totalprice
            payer = []
            totalprice = []

            tip_amount = tip_amount / len(np.unique(payer_list))
            print(tip_amount)
            for key, val in d.items():
                payer.append(key)
                totalprice.append('%.2f' % (np.sum(val) + tip_amount))

            combine = list(zip(payer, totalprice))

            return render_template("index.html",
                                   payer_list=payer_list, combine=combine)
    return render_template("index.html")


@app.route('/pay')
def pay():
    """
    Display venmo QR code for whoever is paying for the items
    """

    qrcode = ["/static/img/Venmo" + p + ".png" for p in payer]

    final = list(zip(payer, totalprice, qrcode))

    return render_template("index.html", final=final)


if __name__ == '__main__':
    # login_manager needs to be initiated before running the app
    login_manager.init_app(app)
    # flask-login uses sessions which require a secret Key
    app.secret_key = os.urandom(24)

    app.debug = True
    app.run(host='0.0.0.0', port=8080)
