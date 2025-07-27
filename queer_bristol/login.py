from datetime import datetime, timedelta, timezone
from functools import wraps
import secrets
from flask import Flask, Request, Response, g, redirect, request, session, url_for

from queer_bristol.extensions import db
from queer_bristol.models import EmailLogin, Session
from queer_bristol.token import generate_token, token_to_id

def init_app(app: Flask):
    @app.before_request
    def load_user():
        session_token = request.cookies.get('login_session')
        session = db.session.get(Session, token_to_id(session_token))

        if session:
            g.user = session.user
            g.session = session

def check_login_link(request: Request):
    login_token = request.args.get("id")
    verify_token = request.args.get("token")
    login = db.session.get(EmailLogin, token_to_id(login_token))
    if not login:
        return None

    if login.expiry < datetime.now(timezone.utc):
        return None

    if not secrets.compare_digest(login.verify_key, token_to_id(verify_token)):
        return None

    return login

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in g:
            session["return_url"] = request.url
            return redirect(url_for('account.login', next=request.url))
        elif "return_url" in session:
            session.pop("return_url")
        return f(*args, **kwargs)
    return decorated_function

def create_session_from_login(login: EmailLogin, response: Response):

    expiry = timedelta(days=14)
    now = datetime.now(timezone.utc)

    session_token = generate_token()

    session = Session(
        id = token_to_id(session_token),
        user = login.user,
        expires = now + expiry
    )

    db.session.add(session)
    db.session.delete(login)
    db.session.commit()

    response.delete_cookie('login_token')
    response.set_cookie('login_session', session_token, expiry, secure=True, httponly=True)