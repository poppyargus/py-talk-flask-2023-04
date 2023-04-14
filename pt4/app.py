import os
import typing as T
from dataclasses import dataclass

import flask
import markupsafe

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
    """class for body template renders"""

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
    # TODO: intentionally looks bad (all nav), for now
    return f"""
<!doctype html>
<title>{params.title}</title>
<nav>
  <h1><a href="{params.url_for_index}">index</a></h1>
  <ul>
      <li><a href="{params.url_for_user}">user {params.user}</a>
      <li><a href="{params.url_for_logout}">logout</a>
      <li><a href="{params.url_for_login}">login</a>
  </ul>
</nav>
<section class="content">
  <header>
      {params.header}
  </header>
  {params.content}
</section>
    """


def get_auth_template_header() -> str:
    return "Log In"


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


def get_user_template_content(messages: list[dict[str, str]]) -> str:
    # TODO: intentionally looks bad (array), for now;
    return f"""
  <div class="messages">
  {messages}
  </div>
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
    header = get_auth_template_header()
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


@app.get("/login")
def login_get():
    return flask.render_template("auth/login.html")
    content = "Should not see this?"
    header = "login"
    user = flask.session.get("user")
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


@app.route("/logout")
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))


@app.route("/user")
@app.route("/user/<user>")
def user_msg(user: T.Optional[str] = None):
    user = markupsafe.escape(user) if user is not None else None
    if user not in users:
        flask.abort(404)
    if user != markupsafe.escape(flask.session.get("user")):
        flask.abort(403)
    content = get_user_template_content(messages[user])
    header = f"User {user}"
    params = get_body_params("user", header, content, user)
    return get_body_template(params)


@app.route("/")
def index():
    content = "Hello, World!"
    header = "index"
    user = flask.session.get("user")
    params = get_body_params("index", header, content, user)
    return get_body_template(params)
