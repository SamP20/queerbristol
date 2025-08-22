


from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
from flask_wtf import FlaskForm
import sqlalchemy as sa
from wtforms import DateField, ValidationError

from queer_bristol.database import local_timezone

from .forms import EventForm
from queer_bristol.extensions import db
from queer_bristol.forms import DeleteConfirmForm
from queer_bristol.login import login_required
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


def combine_event_date_time(form: EventForm) -> tuple[datetime, datetime|None]:
    start_datetime = datetime.combine(
        form.start_date.data,
        form.start_time.data,
        local_timezone()
    )

    end_datetime = None
    if form.end_time.data:
        end_date = form.end_date.data or form.start_date.data
        end_datetime = datetime.combine(
            end_date,
            form.end_time.data,
            local_timezone()
        )

    return (start_datetime, end_datetime)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    group_id = request.args.get('group_id', None)

    group = db.get_or_404(Group, group_id)

    if not g.user.can_admin_group(group):
        abort(403)

    form = EventForm()

    def validate_not_in_past(form: FlaskForm, field: DateField):
        now = datetime.now(tz=local_timezone())
        if field.data and field.data < now.date():
            raise ValidationError("Events cannot be created in the past.")


    if form.validate_on_submit({"start_date": validate_not_in_past}):
        start_datetime, end_datetime = combine_event_date_time(form)

        event = Event(
            title=form.title.data,
            description=form.description.data,
            accessibility=form.accessibility.data,
            start=start_datetime,
            end=end_datetime,
            venue=form.venue.data,
            group=group
        )
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('.event', event_id=event.id))

    cancel_url = url_for('groups.group', group_id=group.id)

    return render_template("events/edit.html", form=form, cancel_url=cancel_url, group=group)

@bp.route("/<int:event_id>/edit", methods=["GET", "POST"])
def edit(event_id):
    event = db.get_or_404(Event, event_id)

    if not g.user.can_admin_group(event.group):
        abort(403)

    form = EventForm(
        obj=event,
        start_date = event.start.date(),
        start_time = event.start.time(),
        end_date = event.end.date() if event.end else None,
        end_time = event.end.time() if event.end else None,
    )

    if form.validate_on_submit():
        start_datetime, end_datetime = combine_event_date_time(form)

        event.start = start_datetime
        event.end = end_datetime
        event.title = form.title.data
        event.description = form.description.data
        event.accessibility = form.accessibility.data
        event.venue = form.venue.data

        db.session.commit()
        return redirect(url_for('.event', event_id=event.id))

    cancel_url = url_for('.event', event_id=event.id)

    return render_template("events/edit.html", form=form, cancel_url=cancel_url, group=event.group)

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
        return redirect(url_for('groups.group', group_id=event.group.id))

    return render_template("events/delete.html", form=form, event=event)
