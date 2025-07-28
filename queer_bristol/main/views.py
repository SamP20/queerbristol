
from datetime import datetime, timedelta, timezone
import secrets
import pytz
from flask import Blueprint, make_response, render_template, abort, request, redirect, url_for
import sqlalchemy as sa

from queer_bristol.extensions import db
from queer_bristol.login import login_required
from queer_bristol.token import generate_token, token_to_id

from .forms import LoginForm, NewEventForm
from queer_bristol.models import Announcement, EmailLogin, Group, Event, Session, User

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

    query = sa.select(Announcement).filter(Announcement.group==group).order_by(Announcement.posted)

    announcements = db.paginate(query)

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

@bp.route("/event/new", methods=["GET", "POST"])
@login_required
def event_new():
    available_groups=db.session.execute(sa.Select(Group)).scalars()

    form = NewEventForm()
    group_list = [(g.id, g.name) for g in available_groups]
    form.group.choices = group_list

    if form.validate_on_submit():
        start_datetime = datetime.combine(
            form.start_date.data,
            form.start_time.data,
            pytz.timezone('Europe/London')
        )

        end_datetime = None
        if form.end_time.data:
            end_date = form.end_date.data or form.start_date.data
            end_datetime = datetime.combine(
                end_date,
                form.end_time.data,
                pytz.timezone('Europe/London')
            )
        event = Event(
            title=form.title.data,
            description=form.description.data,
            start=start_datetime,
            end=end_datetime,
            venue=form.venue.data,
            group_id=form.group.data
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('main.event', event_id=event.id))

    return render_template("main/event_new.html", form=form)

@bp.route("/contact")
def contact():
    return render_template("main/contact.html")