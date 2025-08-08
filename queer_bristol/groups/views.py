


from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, g, redirect, render_template, request, url_for
import sqlalchemy as sa

from queer_bristol.login import login_required

from .forms import GroupForm
from queer_bristol.extensions import db
from queer_bristol.main.views import filter_passthrough_request_args
from queer_bristol.models import Announcement, Event, Group

bp = Blueprint("groups", __name__, url_prefix="/groups")

@bp.route("/")
def index():
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

    paginate_passthrough = filter_passthrough_request_args({"search", "per_page"})

    groups = db.paginate(query)
    return render_template("groups/index.html", groups=groups, paginate_passthrough=paginate_passthrough)

@bp.route("/<int:group_id>")
def group(group_id):
    group = db.get_or_404(Group, group_id)
    now = datetime.now(tz=timezone.utc)

    query = sa.select(Announcement).filter(Announcement.group==group)
    query = query.filter(sa.or_(
        Announcement.hide_after.is_(None),
        Announcement.hide_after < now.date()
    ))
    announcements = db.paginate(query.order_by(Announcement.posted.desc()))

    now = datetime.now(timezone.utc)
    few_hours_ago = now - timedelta(hours=3)

    query = sa.select(Event).filter(sa.and_(
        Event.group==group,
        Event.start>few_hours_ago
    )).order_by(Event.start).limit(1)
    next_event = db.session.execute(query).scalar_one_or_none()

    paginate_passthrough = filter_passthrough_request_args({"search", "per_page"})

    return render_template(
        "groups/group.html",
        group=group,
        announcements=announcements,
        next_event=next_event,
        paginate_passthrough=paginate_passthrough
    )

@bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if not g.user.is_helper:
        abort(403)

    form = GroupForm()

    if form.validate_on_submit():
        group = Group(
            name = form.name.data,
            description = form.description.data,
            tags = form.tags.data
        )

        db.session.add(group)
        db.session.commit()
        return redirect(url_for('.group', group_id=group.id))
    
    cancel_url = url_for('.index')

    return render_template("groups/edit.html", form=form, cancel_url=cancel_url)

@bp.route("/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def edit(group_id):
    group = db.get_or_404(Group, group_id)

    if not g.user.can_admin_group(group):
        abort(403)

    form = GroupForm(obj=group)

    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.tags = form.tags.data
        db.session.commit()
        return redirect(url_for('.group', group_id=group.id))
    
    cancel_url = url_for('.group', group_id=group.id)

    return render_template("groups/edit.html", form=form, cancel_url=cancel_url)
