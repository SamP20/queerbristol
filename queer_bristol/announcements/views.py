


from datetime import datetime, timedelta, timezone, time
from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
import sqlalchemy as sa

from queer_bristol.database import local_timezone
from queer_bristol.extensions import db
from queer_bristol.forms import DeleteConfirmForm
from queer_bristol.login import login_required
from queer_bristol.models import Announcement, Event, Group

from .forms import AnnouncementForm

bp = Blueprint("announcements", __name__, url_prefix="/announcements")

def filter_request_args(filter: set[str]):
    return {k: v for k, v in request.args.items() if k in filter}


@bp.route("/<int:announcement_id>")
def announcement(announcement_id):
    announcement = db.get_or_404(Announcement, announcement_id)
    return render_template("announcements/announcement.html", announcement=announcement)

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    data = {}
    group_id = request.args.get('group_id', None)
    if group_id is not None:
        data["group"] = group_id

    form = AnnouncementForm(data=data)
    if g.user.is_helper:
        available_groups = db.session.execute(sa.Select(Group)).scalars()
    else:
        available_groups = g.user.groups
    group_list = [(g.id, g.name) for g in available_groups]
    form.group.choices = group_list

    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            body=form.body.data,
            posted=datetime.now(tz=timezone.utc),
            group_id=form.group.data,
            hide_after=form.hide_after_date.data
        )
        db.session.add(announcement)
        db.session.commit()
        return redirect(url_for('.announcement', announcement_id=announcement.id))
    
    if group_id is not None:
        cancel_url = url_for('groups.group', group_id=group_id)
    else:
        cancel_url = url_for('groups.index')

    return render_template("announcements/edit.html", form=form, cancel_url=cancel_url)

@bp.route("/<int:announcement_id>/delete", methods=["GET", "POST"])
@login_required
def delete(announcement_id):
    announcement = db.get_or_404(Announcement, announcement_id)

    if not g.user.can_admin_group(announcement.group):
        abort(403)

    form = DeleteConfirmForm()
    if form.validate_on_submit():
        db.session.delete(announcement)
        db.session.commit()
        flash("Announcement deleted")
        return redirect(url_for('groups.group', group_id=announcement.group.id))
    
    return render_template("announcements/delete.html", form=form, announcement=announcement)
