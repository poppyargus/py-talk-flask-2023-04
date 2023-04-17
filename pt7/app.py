import os
import typing as T
import dataclasses
from dataclasses import dataclass
import pytest  # WARN: normally do not do this in prod code

import flask
import markupsafe
import chevron

# pt1: add app, serve index
# pt2: add "messaging" and "user"
# pt3: add "HTML"
# pt4: add login & Session
# pt5: add mustache formatted templating via chevron library
# pt6: add testing NOTE: always at bottom. New code below others, above test
# pt7: add storage abstraction

app = flask.Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")


# "messaging"


users: list[str] = []


def get_user(user: str) -> bool:
    if user in users:
        return True
    return False


def add_user(user: str) -> None:
    if user in users:
        return
    users.append(user)


def seed_users():
    add_user("a")
    add_user("b")


creds: dict[str, str] = {}


def get_cred(user: str) -> T.Optional[str]:
    return creds.get(user)


def set_cred(user: str, cred: str) -> None:
    if not get_user(user):
        raise ValueError("Can't add a cred for a non-existant user")
    # TODO: fabulous place for (external) cred complexity validation
    creds[user] = cred


def check_cred(user: str, cred_in: str) -> bool:
    # TODO: auth will get separated from storage at some point
    cred = get_cred(user)
    # print(user, cred_in, cred)  # NOTE: for debugging fail (missed seed)
    if cred_in == cred:
        return True
    return False


def seed_creds():
    set_cred("a", "1234")
    set_cred("b", "1234")


@dataclass(frozen=True)
class Message:
    frm: str
    msg: str


messages: dict[str, list[Message]] = {}


def get_messages(user: str) -> T.Optional[list[Message]]:
    return messages.get(user)


def add_message(user: str, msg: Message) -> None:
    # NOTE: mutation for the in-memory case, but generally "add to list"
    msgs = messages.get(user)
    if msgs is None:
        msgs = []
        messages[user] = msgs
    msgs.append(msg)


def seed_messages():
    add_message("a", Message("b", "hey"))
    add_message(
        "b",
        Message(
            "a", "weird to write myself for a demo in front of an audience?"
        ),
    )


def seed():
    seed_users()
    seed_creds()
    seed_messages()


# yup, it's all been a global. Someday soon...
seed()


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


def get_user_template_content(messages: list[Message]) -> str:
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
    if not get_user(user):
        flask.abort(404)
    if user != flask.session.get("user"):
        flask.abort(403)
    content = get_user_template_content(get_messages(user))
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
    if check_cred(user, pswd):
        flask.session.clear()
        flask.session["user"] = user
    return flask.redirect(flask.url_for("index"))
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


# test


def test_integration__get_body_template__success_w_user():
    user = "abcdefg"
    # can't use helper - it calls flask, doesn't work outside an `app`!
    # params = get_body_params("", "", "", user)
    _ = ""
    params = ParamsBody(_, _, _, _, _, _, _, user)
    result = get_body_template(params)
    assert "logout" in result
    assert user in result


def test_integration__get_body_template__success_wo_user():
    user = None
    _ = ""
    params = ParamsBody(_, _, _, _, _, _, _, user)
    result = get_body_template(params)
    assert "login" in result
    assert str(user) not in result


@pytest.mark.skip(reason="fails on purpose")
def test_fail():
    raise ValueError("ALWAYS BLUE: yellow")
