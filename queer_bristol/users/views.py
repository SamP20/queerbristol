

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for
import sqlalchemy as sa

from queer_bristol.forms import DeleteConfirmForm
from queer_bristol.login import login_required
from queer_bristol.models import Group, User
from queer_bristol.extensions import db
from queer_bristol.users.forms import UserForm


bp = Blueprint("users", __name__, url_prefix="/users")

@bp.before_request
@login_required
def before_request():
    """ Protect all user admin endpoints. """
    if not g.user.admin:
        abort(403)

def filter_request_args(filter: set[str]):
    return {k: v for k, v in request.args.items() if k in filter}

@bp.route("/")
def index():
    query = sa.select(User).order_by(User.name)

    users = db.paginate(query, per_page=10)

    query_args = filter_request_args({"search"})

    prev_url = url_for('.index', page=users.prev_num, **query_args) if users.has_prev else None # type: ignore
    next_url = url_for('.index', page=users.next_num, **query_args) if users.has_next else None # type: ignore

    return render_template("users/index.html", users=users, prev_url=prev_url, next_url=next_url)

@bp.route("/<int:user_id>")
def user(user_id: int):
    user = db.get_or_404(User, user_id)

    return render_template("users/user.html", user=user)


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
        user.name = form.name.data or ""
        user.email = form.email.data or ""
        user.admin = form.admin.data
        user.helper = form.helper.data
        groups = form.groups.data or []
        user.groups = [groups_by_id[gid] for gid in groups]
        db.session.commit()
        return redirect(url_for('.index'))

    cancel_url = url_for('.index')

    return render_template("users/edit.html", form=form, cancel_url=cancel_url)

@bp.route("/new", methods=["GET", "POST"])
def new():
    form = UserForm()

    query = sa.select(Group).order_by(Group.name)
    groups = db.session.execute(query).scalars()

    form.groups.choices = [
        (g.id, g.name) for g in groups
    ]

    groups_by_id = {g.id: g for g in groups}

    if form.validate_on_submit():
        groups = form.groups.data or []
        user = User(
            name = form.name.data or "",
            email = form.email.data or "",
            admin = form.admin.data,
            helper = form.helper.data,
            groups = [groups_by_id[gid] for gid in groups]
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.user', user_id=user.id))

    cancel_url = url_for('.index')

    return render_template("users/edit.html", form=form, cancel_url=cancel_url)

@bp.route("/<int:user_id>/delete", methods=["GET", "POST"])
def delete(user_id):
    user = db.get_or_404(User, user_id)

    form = DeleteConfirmForm()
    if form.validate_on_submit():
        db.session.delete(user)
        db.session.commit()
        flash("Event deleted")
        return redirect(url_for('.index'))

    cancel_url = url_for('.user', user_id=user.id)

    return render_template("users/delete.html", form=form, user=user, cancel_url=cancel_url)
