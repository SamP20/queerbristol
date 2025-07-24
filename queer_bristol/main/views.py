
from datetime import datetime, timedelta, timezone
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
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    late_previous_day = start_of_day - timedelta(hours=3)
    query = sa.select(Event).order_by(Event.start).filter(Event.start>late_previous_day)

    events = db.paginate(query)
    return render_template("main/events.html", events=events)

@bp.route("/event/<int:event_id>")
def event(event_id):
    event = db.get_or_404(Event, event_id)
    return render_template("main/event.html", event=event)

@bp.route("/contact")
def contact():
    return render_template("main/contact.html")