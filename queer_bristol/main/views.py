
from flask import Blueprint, render_template, abort

from queer_bristol.extensions import db
import sqlalchemy as sa
from .models import Group, Event

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("main/index.html")

@bp.route("/groups")
def groups():
    query = sa.select(Group).order_by(Group.name)
    groups = db.paginate(query)
    return render_template("main/groups.html", groups=groups)

@bp.route("/groups/<group>")
def group(group):
    query = sa.select(Group).filter(Group.slug==group)
    group = db.session.execute(query).scalar_one_or_none()
    if group is None:
        abort(404)

    return render_template("main/group.html", group=group)

@bp.route("/events")
def events():
    return render_template("main/events.html")

@bp.route("/contact")
def contact():
    return render_template("main/contact.html")