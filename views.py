
from flask import Flask, render_template, request, flash
from markupsafe import Markup

app = Flask(__name__)
app.secret_key = 'fgdhSGdhDFHE436SRGf4GEDe@'

@app.route('/test')
def test():
    return render_template("test.html")


@app.route('/Home')
def home():
    return render_template("home.html")


@app.route('/Wall', methods=['POST', 'GET'])
def wall():

    if request.method == 'POST':
        message = request.form['Message']
        email = request.form['Email']
        with open(Flask(__name__).root_path + '/Message.txt', mode='a', encoding='utf-8') as a_file:
            a_file.write(message + ":" + email + "\n")
        flash("Ill put your name on when I can be bothered. So chill out man.", category='info')

    return render_template("old/wall.html")


@app.route('/')
def startUp():
    return render_template("old/startup_page.html")


if __name__ == '__main__':
    app.run()