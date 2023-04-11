import flask

app = flask.Flask(__name__)


@app.route("/")
def hello_world():
    msg = "<p>Hello, World!</p>"
    return msg
