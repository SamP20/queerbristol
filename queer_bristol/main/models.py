
import datetime
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column

from queer_bristol.database import PkModel, UTCDateTime


class Group(PkModel):
    name: Mapped[str]
    description: Mapped[str]
    slug: Mapped[str] = mapped_column(index=True)


class Event(PkModel):
    title: Mapped[str]
    description: Mapped[str]
    start: Mapped[datetime.datetime] = mapped_column(UTCDateTime)
    end: Mapped[Optional[datetime.datetime]] = mapped_column(UTCDateTime)
    venue: Mapped[str]