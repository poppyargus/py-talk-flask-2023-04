import os
import typing as T
import dataclasses
from dataclasses import dataclass
import abc

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


def get_storage_flask():
    # Not my favorite pattern, but from Flask docs,
    # and lifecycle hooks are deprecated
    if "storage" not in flask.g:
        sto = StorageMem()
        seed(sto)
        flask.g.storage = sto
    return flask.g.storage


# "messaging" with storage


@dataclass(frozen=True)
class Message:
    frm: str
    msg: str


# "Abstract base class"; not really OOP. Typeclassing - this is "interface"
# Avoid hierarchic implementation details. `super` is your sign. Use if needed
class Storage(abc.ABC):
    @abc.abstractmethod
    def get_user(self, user: str) -> bool:
        pass

    @abc.abstractmethod
    def add_user(self, user: str) -> None:
        pass

    @abc.abstractmethod
    def get_cred(self, user: str) -> T.Optional[str]:
        pass

    @abc.abstractmethod
    def set_cred(self, user: str, cred: str) -> None:
        pass

    @abc.abstractmethod
    def get_messages(self, user: str) -> T.Optional[list[Message]]:
        pass

    @abc.abstractmethod
    def add_message(self, user: str, msg: Message) -> None:
        pass


# not really OOP, impl of iface, in a land with no interfaces or typeclass...
# (although kind of a weird conversation; in the ways used here, equivalent)
class StorageMem:
    def __init__(self) -> None:
        self.users: list[str] = []
        self.creds: dict[str, str] = {}
        self.messages: dict[str, list[Message]] = {}

    def get_user(self, user: str) -> bool:
        if user in self.users:
            return True
        return False

    def add_user(self, user: str) -> None:
        if user in self.users:
            return
        self.users.append(user)

    def get_cred(self, user: str) -> T.Optional[str]:
        return self.creds.get(user)

    def set_cred(self, user: str, cred: str) -> None:
        if not self.get_user(user):
            raise ValueError("Can't add a cred for a non-existant user")
        # TODO: fabulous place for (external) cred complexity validation
        self.creds[user] = cred

    def get_messages(self, user: str) -> T.Optional[list[Message]]:
        return self.messages.get(user)

    def add_message(self, user: str, msg: Message) -> None:
        # NOTE: mutation for the in-memory case, but generally "add to list"
        msgs = self.messages.get(user)
        if msgs is None:
            msgs = []
            self.messages[user] = msgs
        msgs.append(msg)


# Yes; it is really not inheritance.
Storage.register(StorageMem)


def seed_users(sto: Storage):
    sto.add_user("a")
    sto.add_user("b")


def seed_creds(sto: Storage):
    sto.set_cred("a", "1234")
    sto.set_cred("b", "1234")


def seed_messages(sto: Storage):
    sto.add_message("a", Message("b", "hey"))
    sto.add_message(
        "b",
        Message(
            "a", "weird to write myself for a demo in front of an audience?"
        ),
    )


def seed(sto: Storage):
    seed_users(sto)
    seed_creds(sto)
    seed_messages(sto)


def check_cred(sto: Storage, user: str, cred_in: str) -> bool:
    cred = sto.get_cred(user)
    # print(user, cred_in, cred)  # NOTE: for debugging fail (missed seed)
    if cred_in == cred:
        return True
    return False


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
    title: str, header: str, content: str, user: T.Optional[str]
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
    sto = get_storage_flask()
    if not sto.get_user(user):
        flask.abort(404)
    if user != flask.session.get("user"):
        flask.abort(403)
    content = get_user_template_content(sto.get_messages(user))
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


@app.get("/login")
def login_get():
    content = get_auth_template_content()
    header = "login"
    user = flask.session.get("user")
    params = get_body_params("index", header, content, user)
    return get_body_template(params)


@app.post("/login")
def login_post():
    user = flask.request.form.get("username")
    pswd = flask.request.form.get("password")
    sto = get_storage_flask()
    if user is None:
        flask.abort(403)
    if check_cred(sto, user, pswd):
        flask.session.clear()
        flask.session["user"] = user
    return flask.redirect(flask.url_for("index"))


@app.route("/logout")
def logout():
    flask.session.clear()
    return flask.redirect(flask.url_for("index"))


# test


def test_unit__get_user__fail_missing():
    sto = StorageMem()
    assert not sto.get_user("a")


def test_unit__add_user__get_user_success():
    sto = StorageMem()
    sto.add_user("a")
    assert sto.get_user("a")


def test_unit__get_cred__fail_missing():
    sto = StorageMem()
    sto.add_user("a")
    assert not sto.get_cred("a")


def test_unit__set_cred__get_cred_success():
    sto = StorageMem()
    sto.add_user("a")
    sto.set_cred("a", "1234")
    assert sto.get_cred("a") == "1234"


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
