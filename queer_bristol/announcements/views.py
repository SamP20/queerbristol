


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
    group_id = request.args.get('group_id', None)

    group = db.get_or_404(Group, group_id)

    if not g.user.can_admin_group(group):
        abort(403)

    form = AnnouncementForm()

    if form.validate_on_submit():
        announcement = Announcement(
            title=form.title.data,
            body=form.body.data,
            posted=datetime.now(tz=timezone.utc),
            group=group,
            hide_after=form.hide_after.data
        )
        db.session.add(announcement)
        db.session.commit()
        return redirect(url_for('.announcement', announcement_id=announcement.id))
    
    cancel_url = url_for('groups.group', group_id=group.id)

    return render_template("announcements/edit.html", form=form, cancel_url=cancel_url)


@bp.route("/<int:announcement_id>/edit", methods=["GET", "POST"])
@login_required
def edit(announcement_id):
    announcement = db.get_or_404(Announcement, announcement_id)

    if not g.user.can_admin_group(announcement.group):
        abort(403)

    form = AnnouncementForm(obj=announcement)

    if form.validate_on_submit():
        announcement.title = form.title.data
        announcement.body = form.body.data
        announcement.hide_after = form.hide_after.data

        db.session.commit()
        return redirect(url_for('.announcement', announcement_id=announcement.id))
    
    cancel_url = url_for('.announcement', announcement_id=announcement.id)

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
