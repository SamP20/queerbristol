

from flask import Blueprint, redirect, render_template, request, url_for
import sqlalchemy as sa

from queer_bristol.models import Group, User
from queer_bristol.extensions import db
from queer_bristol.users.forms import UserForm


bp = Blueprint("users", __name__, url_prefix="/users")

def filter_request_args(filter: set[str]):
    return {k: v for k, v in request.args.items() if k in filter}

@bp.route("/")
def index():
    query = sa.select(User).order_by(User.name)

    users = db.paginate(query, per_page=10)

    query_args = filter_request_args({"search"})

    prev_url = url_for('.index', page=users.prev_num, **query_args) if users.has_prev else None
    next_url = url_for('.index', page=users.next_num, **query_args) if users.has_next else None

    return render_template("users/index.html", users=users, prev_url=prev_url, next_url=next_url)

@bp.route("/<int:user_id>/edit", methods=["GET", "POST"])
def edit(user_id):
    user = db.get_or_404(User, user_id)

    form = UserForm(obj=user, groups=[g.id for g in user.groups])

    query = sa.select(Group).order_by(Group.name)
    groups = db.session.execute(query).scalars()

    form.groups.choices = [
        (g.id, g.name) for g in groups
    ]

    groups_by_id = {g.id: g for g in groups}

    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.admin = form.admin.data
        user.helper = form.helper.data
        user.groups = [groups_by_id[gid] for gid in form.groups.data]
        db.session.commit()
        return redirect(url_for('.index'))
    
    cancel_url = url_for('.index')

    return render_template("users/edit.html", form=form, cancel_url=cancel_url)