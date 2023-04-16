import os
import typing as T
import dataclasses
from dataclasses import dataclass

import flask
import markupsafe
import chevron

app = flask.Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

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


def get_user_template_content(messages: list[dict[str, str]]) -> str:
    tmpl = """
    <div class="messages">
    {{{messages}}}
    </div>
    """
    return chevron.render(tmpl, {"messages": messages})


@app.route("/user/<user>")
def user_msg(user: T.Optional[str] = None):
    user = markupsafe.escape(user) if user is not None else None
    if user not in users:
        flask.abort(404)
    if user != flask.session.get("user"):
        flask.abort(403)
    content = get_user_template_content(messages[user])
    header = "User messages"
    params = get_body_params("user", header, content, user)
    return get_body_template(params)


def get_auth_template_content() -> str:
    tmpl = """
<form method="post">
    <label for="username">Username</label>
    <input name="username" id="username" required>
    <label for="password">Password</label>
    <input type="password" name="password" id="password" required>
    <input type="submit" value="Log In">
</form>
    """
    return tmpl


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
    header = "login"
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
