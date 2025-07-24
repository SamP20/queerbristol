
import datetime
from typing import Optional
from sqlalchemy import Computed, ForeignKey, Index, String, literal, literal_column
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func


from queer_bristol.database import PkModel, UTCDateTime


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