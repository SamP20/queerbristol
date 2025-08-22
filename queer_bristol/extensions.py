from flask import current_app, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from scaleway import Client as ScalewayClient
from werkzeug.local import LocalProxy

db = SQLAlchemy()
migrate = Migrate(db=db)

def get_scaleway() -> ScalewayClient:
    if 'scaleway' not in g:
        g.scaleway = ScalewayClient(
            access_key=current_app.config["SCALEWAY_ACCESS_KEY"],
            secret_key=current_app.config["SCALEWAY_SECRET_KEY"],
            default_project_id=current_app.config["SCALEWAY_PROJECT_ID"],
            default_region=current_app.config["SCALEWAY_REGION"],
            default_zone=current_app.config["SCALEWAY_ZONE"],
        )
    return g.scaleway

scaleway = LocalProxy(get_scaleway)