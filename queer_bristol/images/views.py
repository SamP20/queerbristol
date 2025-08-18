from flask import Blueprint, render_template, url_for

from queer_bristol.extensions import db
from queer_bristol.images.forms import ImageUploadForm
from queer_bristol.models import Group


bp = Blueprint("images", __name__, url_prefix="/images")

@bp.route("/by-group/<int:group_id>")
def by_group(group_id):
    group = db.get_or_404(Group, group_id)


@bp.route("/by-group/<int:group_id>/upload", methods=["GET", "POST"])
def upload(group_id):
    group = db.get_or_404(Group, group_id)

    form = ImageUploadForm()

    if form.validate_on_submit():
        pass

    cancel_url = url_for('.by_group', group_id=group.id)

    return render_template("images/upload.html", form=form, cancel_url=cancel_url)