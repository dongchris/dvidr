from flask import Flask, render_template

app = Flask(__name__)

@app.route("/dvidr")
def homepage():
    """Show a list of article titles"""
    return render_template('homepage.html')

@app.route("/dvidr/login")
def user_login():
    """Show a list of article titles"""
    return render_template('login.html')

@app.route("/dvidr/upload")
def upload_image():
    """Show a list of article titles"""
    return render_template('upload.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
#app.run(host='localhost', port=80)