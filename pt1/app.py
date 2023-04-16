import flask

# pt1: add app, serve index

app = flask.Flask(__name__)


# index


@app.route("/")
def index():
    msg = "<p>Hello, World!</p>"
    return msg
