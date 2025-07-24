
from flask import Blueprint, render_template, abort, request

from queer_bristol.extensions import db
import sqlalchemy as sa
from .models import Group, Event

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("main/index.html")

@bp.route("/groups")
def groups():
    search = request.args.get('search')

    if search:
        tsquery = sa.func.plainto_tsquery(sa.literal('english'), search)
        tsrank = sa.func.ts_rank(Group.search_vector, tsquery, 0).label('rank_tags')
        query = sa.select(
            Group,
            tsrank
        )
        
        query = query.filter(Group.search_vector.op('@@')(tsquery))
        query = query.order_by(tsrank.desc())
    else:
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
    query = sa.select(Event).order_by(Event.start).filter(Event.start)
    return render_template("main/events.html")

@bp.route("/contact")
def contact():
    return render_template("main/contact.html")