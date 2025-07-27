
from datetime import datetime, timedelta, timezone
import secrets
from flask import Blueprint, flash, g, make_response, redirect, render_template, request, session, url_for
import sqlalchemy as sa

from queer_bristol.extensions import db
from queer_bristol.login import check_login_link, create_session_from_login
from queer_bristol.token import generate_token, token_to_id

from .forms import LoginForm
from queer_bristol.models import EmailLogin, Session, User

bp = Blueprint("account", __name__, url_prefix="/account")

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login_token = generate_token()
        verify_token = generate_token()
        expiry = timedelta(hours=1)
        now = datetime.now(timezone.utc)

        query = sa.select(User).filter(User.email==form.email.data)
        user = db.session.execute(query).scalar_one_or_none()

        login = EmailLogin(
            id = token_to_id(login_token),
            verify_key = token_to_id(verify_token),
            visual_code = str(secrets.randbelow(100000)).zfill(5),
            expiry = expiry + now,
            verified = False,
            user = user
        )

        db.session.add(login)
        db.session.commit()

        verify_url = url_for('account.login_verify', _external=True, id=login_token, token=verify_token)

        login_redirect = session.get("return_url") or url_for('main.index')

        response = make_response(render_template(
            "account/login_wait.html",
            login=login,
            verify_url=verify_url,
            login_poll_url=url_for('account.login_check'),
            login_redirect=login_redirect,
        ))
        response.set_cookie('login_token', login_token, expiry, secure=True, httponly=True)
        return response

    return render_template("account/login.html", form=form)

@bp.route("/login_verify", methods=["GET", "POST"])
def login_verify():
    login = check_login_link(request)
    needs_confirmation = True

    if login:
        # We have a confirm button as some email providers (*cough* Microsoft *cough*) now open all links in emails
        # If the link was opened in the same browser as the login request then we can skip this step
        skip_confirm_button = request.cookies.get('login_token') == request.args.get("id")
        if skip_confirm_button or request.method == "POST":
            login.verified = True
            db.session.commit()
            needs_confirmation = False

    return render_template("account/login_verify.html", login=login, needs_confirmation=needs_confirmation)


@bp.route("/login_check")
def login_check():
    login_token = request.cookies.get('login_token')

    login = db.session.get(EmailLogin, token_to_id(login_token))

    if login and login.verified:
        response = make_response({"verified": True})

        create_session_from_login(login, response)

        return response
    else:
        return {"verified": False}

@bp.route("/logout")
def logout():
    db.session.delete(g.session)
    db.session.commit()
    flash('You were successfully logged out')
    response = make_response(redirect(url_for('main.index')))
    response.delete_cookie('login_session')
    return response