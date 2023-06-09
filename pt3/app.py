import typing as T
from dataclasses import dataclass

import flask
import markupsafe

# pt1: add app, serve index
# pt2: add "messaging" and "user"
# pt3: add "HTML"

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


@dataclass(frozen=True)
class ParamsBody:
    title: str
    url_for_index: str
    header: T.Optional[str]
    content: T.Optional[str]


def get_body_params(title: str, header: str, content: str) -> ParamsBody:
    return ParamsBody(
        title,
        flask.url_for("index"),
        header,
        content,
    )


def get_body_template(params: ParamsBody) -> str:
    # TODO: intentionally looks bad (all nav), for now
    return f"""
<!doctype html>
<title>{params.title}</title>
<nav>
    <h1><a href="{params.url_for_index}">index</a></h1>
</nav>
<section class="content">
    <header>
        {params.header}
    </header>
    {params.content}
</section>
    """


@app.route("/")
def index():
    content = "Hello, World!"
    header = "index"
    params = get_body_params("index", header, content)
    return get_body_template(params)


# user


def get_user_template_content(messages: list[dict[str, str]]) -> str:
    # TODO: intentionally looks bad (array), for now;
    return f"""
<div class="messages">
{messages}
</div>
    """


@app.route("/user")
@app.route("/user/<user>")
def user_msg(user: T.Optional[str] = None):
    user = markupsafe.escape(user) if user is not None else None
    if user not in users:
        flask.abort(404)
    content = get_user_template_content(messages[user])
    header = f"User {user}"
    params = get_body_params("user", header, content)
    return get_body_template(params)
