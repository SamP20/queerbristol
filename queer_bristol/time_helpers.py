

from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Blueprint, current_app

bp = Blueprint('time_helpers', __name__, cli_group=None)

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