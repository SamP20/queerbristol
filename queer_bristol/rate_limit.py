
from sqlalchemy import delete, and_
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta, timezone

from queer_bristol.models import RateLimit
from queer_bristol.extensions import db

def attempt(key: str, limit: int, expiry_secs: int) -> bool:
    now = datetime.now(timezone.utc)
    expiry = now + timedelta(seconds=expiry_secs)

    # Delete any expired rate limits first
    db.session.execute(delete(RateLimit).where(and_(
        RateLimit.key==key,
        RateLimit.expire < now
    )))

    stmt = insert(RateLimit).values(
        key=key,
        limit=limit,
        count=1,
        expire=expiry
    )

    stmt = stmt.on_conflict_do_update(
        index_elements=[RateLimit.key],
        set_=dict(
            count=RateLimit.count+1
        )
    ).returning(RateLimit)

    result = db.session.scalars(stmt).first()

    return result.count < result.limit