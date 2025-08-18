
import datetime
from typing import Optional
from sqlalchemy import Column, Computed, Date, DateTime, ForeignKey, Index, String, Table, literal, literal_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func, expression


from queer_bristol.database import LocalDateTime, PkModel, UTCDateTime
from queer_bristol.extensions import db


# class RateLimit():
#     key: Mapped[str] = mapped_column(primary_key=True)
#     limit: Mapped[int]
#     count: Mapped[int]
#     expire: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))

class Group(PkModel):
    name: Mapped[str]
    description: Mapped[str]
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
    accessibility: Mapped[str] = mapped_column(String, server_default="")
    start: Mapped[datetime.datetime] = mapped_column(LocalDateTime)
    end: Mapped[Optional[datetime.datetime]] = mapped_column(LocalDateTime)
    venue: Mapped[str]
    group_id: Mapped[Optional[int]] = mapped_column(ForeignKey("group.id", onupdate="CASCADE", ondelete="CASCADE"))

    group: Mapped[Optional["Group"]] = relationship()

    def format_start_end(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        time_fmt = "%H:%M"
        if self.start.year != now.year:
            start_date = self.start.strftime("%a %-d %b %Y")
        else:
            start_date = self.start.strftime("%a %-d %b")
        start_time = self.start.strftime(time_fmt)

        if self.end is None:
            return f"{start_date} {start_time}"
        else:
            if self.end.year != now.year:
                end_date = self.end.strftime("%a %-d %b %Y")
            else:
                end_date = self.end.strftime("%a %-d %b")

            end_time = self.end.strftime(time_fmt)
            
            if self.end.date() == self.start.date():
                return f"{start_date} {start_time} - {end_time}"
            else:
                return f"{start_date} {start_time} - {end_date} {end_time}"



class Announcement(PkModel):
    title: Mapped[str]
    body: Mapped[str]
    posted: Mapped[datetime.datetime] = mapped_column(LocalDateTime)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id", onupdate="CASCADE", ondelete="CASCADE"))
    hide_after: Mapped[Optional[datetime.date]] = mapped_column(Date)

    group: Mapped[Optional["Group"]] = relationship()

    def format_posted(self):
        now = datetime.datetime.now(tz=datetime.timezone.utc)

        time_fmt = "%H:%M"
        if self.posted.year != now.year:
            posted_date = self.posted.strftime("%a %-d %b %Y")
        else:
            posted_date = self.posted.strftime("%a %-d %b")
        posted_time = self.posted.strftime(time_fmt)

        return f"{posted_date} {posted_time}"

    __table_args__ = (
        Index(
            'ix_announcement_posted',
            posted,
            postgresql_using='brin'
        ),
    )

user_group_association = Table(
    "user_group",
    db.Model.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("group_id", ForeignKey("group.id"), primary_key=True)
)


class User(PkModel):
    email: Mapped[str] = mapped_column(index=True, unique=True)
    name: Mapped[str]
    admin: Mapped[bool] = mapped_column(server_default=expression.false())
    helper: Mapped[bool] = mapped_column(server_default=expression.false())

    groups: Mapped[list["Group"]] = relationship('Group', secondary=user_group_association)

    @hybrid_property
    def is_helper(self):
        return self.admin or self.helper
    
    def can_admin_group(self, group: Group):
        return self.is_helper or group in self.groups

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

class Image(db.Model):
    id: Mapped[str] = mapped_column(primary_key=True) # Will be the saved image hash
    name: Mapped[str]
    alt_text: Mapped[str] = mapped_column(server_default="")