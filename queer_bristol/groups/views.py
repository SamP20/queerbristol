


from datetime import datetime, timedelta, timezone
from flask import Blueprint, abort, g, redirect, render_template, request, url_for
import sqlalchemy as sa

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

    query = sa.select(Announcement).filter(Announcement.group==group).order_by(Announcement.posted.desc())
    announcements = db.paginate(query)

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

@bp.route("/<int:group_id>/edit", methods=["GET", "POST"])
def edit(group_id):
    group = db.get_or_404(Group, group_id)

    if not ('user' in g and g.user.can_admin_group(group)):
        abort(403)

    form = GroupForm(obj=group)

    if form.validate_on_submit():
        group.name = form.name.data
        group.description = form.description.data
        group.tags = form.tags.data
        group.slug = form.slug.data
        db.session.commit()
        return redirect(url_for('.group', group_id=group.id))

    return render_template("groups/edit.html", form=form, group=group)
