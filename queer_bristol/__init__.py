import logging
import os
import sys
import tomllib

from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="postgresql+psycopg2://postgres:postgres@localhost:5432/queer_bristol",
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_file("config.toml", load=tomllib.load, text=False, silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    register_extensions(app)
    register_blueprints(app)
    configure_logger(app)

    return app


def register_extensions(app: Flask):
    from .extensions import db, migrate
    from flask_session.sqlalchemy import SqlAlchemySessionInterface
    db.init_app(app)
    migrate.init_app(app)
    app.session_interface = SqlAlchemySessionInterface(app, db)


def register_blueprints(app: Flask):
    from queer_bristol import main
    app.register_blueprint(main.views.bp)

def configure_logger(app):
    """Configure loggers."""
    handler = logging.StreamHandler(sys.stdout)
    if not app.logger.handlers:
        app.logger.addHandler(handler)