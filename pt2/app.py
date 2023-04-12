import flask
import markupsafe

app = flask.Flask(__name__)

users = [
    "poppyargus2023+sec1@calmspark.org",
    "poppyargus2023+sec2@calmspark.org",
]

creds = {
    "poppyargus2023+sec1@calmspark.org": "1234",
    "poppyargus2023+sec2@calmspark.org": "1234",
}

messages = {
    "poppyargus2023+sec1@calmspark.org": [
        {
            "from": "poppyargus2023+sec2@calmspark.org",
            "msg": "hey",
        },
    ],
    "poppyargus2023+sec2@calmspark.org": [
        {
            "from": "poppyargus2023+sec1@calmspark.org",
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
