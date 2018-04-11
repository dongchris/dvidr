from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def homepage():
    """Show homepage"""
    return render_template('homepage.html')

@app.route("/login")
def user_login():
    """Login / Register page -- not yet implemented"""
    return render_template('login.html')

if __name__ == '__main__':
    app.debug = True
    app.run()
# app.run(host='localhost', port=80)