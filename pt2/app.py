import typing as T

import flask
import markupsafe

# pt1: add app, serve index
# pt2: add "messaging" and "user"

app = flask.Flask(__name__)


# "messaging"

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


# index


@app.route("/")
def index():
    msg = "<p>Hello, World!</p>"
    return msg


# user


@app.route("/user")
@app.route("/user/<user>")
def user_msg(user: T.Optional[str] = None):
    user = markupsafe.escape(user) if user is not None else None
    if user not in users:
        flask.abort(404)
    return f"User {user} {messages[user]}"
