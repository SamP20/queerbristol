
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Blueprint, current_app, flash, g, make_response, render_template, abort, request, redirect, url_for
import sqlalchemy as sa

from queer_bristol.extensions import db
from queer_bristol.login import login_required
from queer_bristol.token import generate_token, token_to_id

from queer_bristol.models import Announcement, EmailLogin, Group, Event, Session, User

bp = Blueprint("main", __name__)


def filter_passthrough_request_args(passthrough: set[str]):
    return {k: v for k, v in request.args.items() if k in passthrough}

def current_timezone():
    zone = current_app.config.get("TIMEZONE", "Europe/London")
    return ZoneInfo(zone)

@bp.app_template_filter('localtime')
def localtime(t: datetime):
    return t.astimezone(current_timezone())

@bp.app_template_filter('datetime_to_human')
def datetime_to_human(t: datetime):
    tz = current_timezone()
    t = t.astimezone(tz)
    fmt = '%-d %B %Y %H:%M %Z'
    return t.strftime(fmt)


@bp.route("/")
def index():
    return render_template("main/index.html")


@bp.route("/contact")
def contact():
    return render_template("main/contact.html")