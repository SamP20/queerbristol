from base64 import urlsafe_b64encode
from math import floor
import os
from pathlib import Path
from PIL import Image as PilImage
from flask import Blueprint, current_app, redirect, render_template, request, send_from_directory, url_for
import sqlalchemy as sa
import uuid
from werkzeug.datastructures import FileStorage

from queer_bristol.extensions import db
from queer_bristol.images.forms import ImageUploadForm
from queer_bristol.models import Group, Image


bp = Blueprint("images", __name__, url_prefix="/images")

@bp.route("/<uuid:image_id>")
def image(image_id):
    image = db.get_or_404(Image, image_id)

    upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
    image_path = upload_folder / "images"

    return send_from_directory(image_path, image.filename())

@bp.route("/by-group/<int:group_id>")
def by_group(group_id):
    group = db.get_or_404(Group, group_id)

    query = sa.select(Image).filter(Image.group==group)
    images = db.paginate(query)

    prev_url = url_for('.by_group', page=images.prev_num, group_id=group.id) if images.has_prev else None
    next_url = url_for('.by_group', page=images.next_num, group_id=group.id) if images.has_next else None

    view_mode = request.args.get("view_mode")

    return render_template("images/list.html", group=group, images=images, prev_url=prev_url, next_url=next_url, view_mode=view_mode)


@bp.route("/by-group/<int:group_id>/upload", methods=["GET", "POST"])
def upload(group_id):
    group = db.get_or_404(Group, group_id)

    form = ImageUploadForm()

    if form.validate_on_submit():
        f: FileStorage = form.image.data

        upload_folder = Path(current_app.root_path) / current_app.config["UPLOAD_FOLDER"]
        image_path = upload_folder / "images"
        image_path.mkdir(parents=True, exist_ok=True)

        image_id = uuid.uuid4()

        image = PilImage.open(f.stream)

        extension = "png" if image.format == "PNG" else "jpeg"
    

        max_width = current_app.config.get("IMAGE_MAX_WIDTH", 960)
        max_height = current_app.config.get("IMAGE_MAX_HEIGHT", 540)

        new_size = image.size

        if image.width > max_width or image.height > max_height:
            width_scale = max_width / image.width
            height_scale = max_height / image.height
            if width_scale < height_scale:
                new_size = (max_width, round(image.height * width_scale))
            else:
                new_size = (round(image.width * height_scale), max_height)
            image = image.resize(new_size)

        image_model = Image(
            id = image_id,
            extension = extension,
            name = form.name.data,
            alt_text = form.alt_text.data or "",
            group = group
        )
        db.session.add(image_model)
        db.session.commit()



        image.save(image_path / image_model.filename())

        return redirect(url_for('.by_group', group_id=group.id))

    cancel_url = url_for('.by_group', group_id=group.id)

    return render_template("images/upload.html", form=form, cancel_url=cancel_url)