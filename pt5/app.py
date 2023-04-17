import os
import typing as T
import dataclasses
from dataclasses import dataclass

import flask
import markupsafe
import chevron

# pt1: add app, serve index
# pt2: add "messaging" and "user"
# pt3: add "HTML"
# pt4: add login & Session
# pt5: add mustache formatted templating via chevron library

app = flask.Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


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


@dataclass(frozen=True)
class ParamsBody:
    title: str
    url_for_index: str
    url_for_login: str
    url_for_logout: str
    url_for_user: str
    header: T.Optional[str]
    content: T.Optional[str]
    user: T.Optional[str]


def get_body_params(
    title: str, header: str, content: str, user: str
) -> ParamsBody:
    return ParamsBody(
        title,
        flask.url_for("index"),
        flask.url_for("login_get"),
        flask.url_for("logout"),
        flask.url_for("user_msg", user=user),
        header,
        content,
        user,
    )


def get_body_template(params: ParamsBody) -> str:
    tmpl = """
<!doctype html>
<title>{{title}}</title>
<nav>
    <h1><a href="{{url_for_index}}">index</a></h1>
    <ul>
        {{#user}}
            <li><a href="{{url_for_user}}">user {{user}}</a>
            <li><a href="{{url_for_logout}}">logout</a>
        {{/user}}
        {{^user}}
            <li><a href="{{url_for_login}}">login</a>
        {{/user}}
    </ul>
</nav>
<section class="content">
    <header>
        {{{header}}}
    </header>
    {{{content}}}
</section>
    """
    return chevron.render(tmpl, dataclasses.asdict(params))


@app.route("/")
def index():
    content = "Hello, World!"
    header = "index"
    user = flask.session.get("user")
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


# user


def get_user_template_content(messages: list[dict[str, str]]) -> str:
    # TODO: could look much better; later
    tmpl = """
<div class="messages">
{{{messages}}}
</div>
    """
    return chevron.render(tmpl, {"messages": messages})


@app.route("/user")
@app.route("/user/<user>")
def user_msg(user: T.Optional[str] = None):
    user = str(markupsafe.escape(user)) if user is not None else None
    if user not in users:
        flask.abort(404)
    if user != flask.session.get("user"):
        flask.abort(403)
    content = get_user_template_content(messages[user])
    header = f"User {user}"
    params = get_body_params("user", header, content, user)
    result = get_body_template(params)
    # print(result)  # this is how I debugged the markupsafe issue
    return result


# auth: login & logout


def get_auth_template_content() -> str:
    return """
<form method="post">
    <label for="username">Username</label>
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Log In">
</form>
    """


@app.post("/login")
def login_post():
    user = flask.request.form.get("username")
    pswd = flask.request.form.get("password")
    if user is None:
        flask.abort(403)
    if creds[user] == pswd:
        flask.session.clear()
        flask.session["user"] = user
    content = get_auth_template_content()
    header = "Log In"
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


@app.get("/login")
def login_get():
    content = get_auth_template_content()
    header = "login"
    user = flask.session.get("user")
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


@app.route("/logout")
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))
