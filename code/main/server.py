from flask import Flask, render_template

app = Flask(__name__, template_folder = '../templates', static_folder = '../static')

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