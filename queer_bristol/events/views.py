


from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
import sqlalchemy as sa

from .forms import EventForm
from queer_bristol.extensions import db
from queer_bristol.forms import DeleteConfirmForm
from queer_bristol.login import login_required
from queer_bristol.time_helpers import current_timezone
from queer_bristol.models import Event, Group

bp = Blueprint("events", __name__, url_prefix="/events")

def filter_request_args(filter: set[str]):
    return {k: v for k, v in request.args.items() if k in filter}

@bp.route("/")
def index():
    now = datetime.now(timezone.utc)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    late_previous_day = start_of_day - timedelta(hours=3)
    query = sa.select(Event).order_by(Event.start).filter(Event.start>late_previous_day)

    group_id = request.args.get("group_id")
    if group_id is not None:
        query = query.filter(Event.group_id==group_id)

    events = db.paginate(query, per_page=10)

    query_args = filter_request_args({"group_id"})

    prev_url = url_for('.index', page=events.prev_num, **query_args) if events.has_prev else None
    next_url = url_for('.index', page=events.next_num, **query_args) if events.has_next else None

    return render_template("events/index.html", events=events, prev_url=prev_url, next_url=next_url)

@bp.route("/<int:event_id>")
def event(event_id):
    event = db.get_or_404(Event, event_id)
    return render_template("events/event.html", event=event)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    data = {}
    group_id = request.args.get('group', None)
    if group_id is not None:
        data["group"] = group_id

    form = EventForm(data=data)
    if g.user.is_helper:
        available_groups = db.session.execute(sa.Select(Group)).scalars()
    else:
        available_groups = g.user.groups
    group_list = [(g.id, g.name) for g in available_groups]
    form.group.choices = group_list

    if form.validate_on_submit():
        start_datetime = datetime.combine(
            form.start_date.data,
            form.start_time.data,
            current_timezone()
        )

        end_datetime = None
        if form.end_time.data:
            end_date = form.end_date.data or form.start_date.data
            end_datetime = datetime.combine(
                end_date,
                form.end_time.data,
                current_timezone()
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
        return redirect(url_for('.index', event_id=event.id))

    return render_template("events/new.html", form=form)

@bp.route("/<int:event_id>/delete", methods=["GET", "POST"])
@login_required
def delete(event_id):
    event = db.get_or_404(Event, event_id)

    if not g.user.can_admin_group(event.group):
        abort(403)

    form = DeleteConfirmForm()
    if form.validate_on_submit():
        db.session.delete(event)
        db.session.commit()
        flash("Event deleted")
        return redirect(url_for('main.group', group_slug=event.group.full_slug))
    
    return render_template("events/delete.html", form=form, event=event)
