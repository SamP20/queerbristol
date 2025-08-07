import datetime
from sqlalchemy import types
from sqlalchemy.orm import Mapped, mapped_column

from queer_bristol.extensions import db

Model = db.Model


class SpaceSeparatedSet(types.TypeDecorator):

    impl = types.String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value:
            return " ".join(value)
        else:
            return ""

    def process_result_value(self, value, dialect):
        if value:
            return set(value.split())
        else:
            return set()


class PkModel(Model):
    """Base model with a primary key column named ``id``."""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)

