import flask
import markupsafe

app = flask.Flask(__name__)


users = [
    "a",
    "b",
]

creds = {
    "a": "1234",
    "b": "1234",
}

messages = {
    "a": [
        {
            "from": "b",
            "msg": "hey",
        },
    ],
    "b": [
        {
            "from": "a",
            "msg": "weird to write myself for a demo in front of an audience?",
        },
    ],
}


@app.route("/user/<user>")
def show_user(user):
    escuser = markupsafe.escape(user)
    if escuser not in users:
        flask.abort(404)
    return f"User {escuser}"


@app.route("/")
def root():
    msg = "<p>Hello, World!</p>"
    return msg
