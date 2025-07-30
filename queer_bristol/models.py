
import datetime
from typing import Optional
from sqlalchemy import Computed, ForeignKey, Index, String, literal, literal_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, expression


from queer_bristol.database import PkModel, UTCDateTime
from queer_bristol.extensions import db


# class RateLimit():
#     key: Mapped[str] = mapped_column(primary_key=True)
#     limit: Mapped[int]
#     count: Mapped[int]
#     expire: Mapped[datetime.datetime] = mapped_column(UTCDateTime)

class UserGroup(db.Model):
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)
    group_id: Mapped[int] =  mapped_column(ForeignKey("group.id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True)

    group: Mapped["Group"] = relationship()

class Group(PkModel):
    name: Mapped[str]
    description: Mapped[str]
    slug: Mapped[str] = mapped_column(index=True)
    tags: Mapped[str] = mapped_column(String, server_default="")

    search_vector: Mapped[str] = mapped_column(TSVECTOR, Computed(
        func.setweight(func.to_tsvector(literal('english'), literal_column('name')), 'A')
        .concat(func.setweight(func.to_tsvector(literal('english'), literal_column('tags')), 'B'))
        .concat(func.setweight(func.to_tsvector(literal('english'), literal_column('description')), 'C')),
        persisted=True
    ))

    __table_args__ = (
        Index(
            'ix_group_tags',
            search_vector,
            postgresql_using='gin'
        ),
    )


class Event(PkModel):
    title: Mapped[str]
    description: Mapped[str]
    start: Mapped[datetime.datetime] = mapped_column(UTCDateTime)
    end: Mapped[Optional[datetime.datetime]] = mapped_column(UTCDateTime)
    venue: Mapped[str]
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("group.id", onupdate="CASCADE", ondelete="CASCADE"))


    group: Mapped[Optional["Group"]] = relationship()


class Announcement(PkModel):
    title: Mapped[str]
    body: Mapped[str]
    posted: Mapped[datetime.datetime] = mapped_column(UTCDateTime)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id", onupdate="CASCADE", ondelete="CASCADE"))

    group: Mapped[Optional["Group"]] = relationship()

    __table_args__ = (
        Index(
            'ix_announcement_posted',
            posted,
            postgresql_using='brin'
        ),
    )


class User(PkModel):
    email: Mapped[str] = mapped_column(index=True, unique=True)
    name: Mapped[str]
    admin: Mapped[bool] = mapped_column(server_default=expression.false())
    helper: Mapped[bool] = mapped_column(server_default=expression.false())

    groups: Mapped[list["Group"]] = relationship('Group', secondary=UserGroup.__table__, backref='user')

class Session(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    expires: Mapped[datetime.datetime] = mapped_column(UTCDateTime)

    user: Mapped["User"] = relationship()


class EmailLogin(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user.id", onupdate="CASCADE", ondelete="CASCADE"))
    verify_key: Mapped[str]
    visual_code: Mapped[str] # A code the user can visually check matches the one in the email

    expiry: Mapped[datetime.datetime] = mapped_column(UTCDateTime)
    verified: Mapped[bool]

    user: Mapped[Optional["User"]] = relationship()
