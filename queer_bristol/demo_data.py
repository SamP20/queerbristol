from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import click
from flask import Flask, Blueprint

from queer_bristol.extensions import db
from queer_bristol.models import Event, Group, User

bp = Blueprint('demo', __name__, cli_group=None)


@bp.cli.command("make-demo-data")
@click.argument('name')
@click.argument('email')
def make_demo_data(name: str, email: str):
    db.drop_all()
    db.create_all()

    db.session.add(User(
        email = email,
        name = name,
        admin = True
    ))

    climbing = Group(
            name="Generic Climbing Group",
            description="We climb on occasion, both indoors and outdoors.",
            tags="climbing fitness sport bouldering ropes"
    )
    hiking = Group(
        name="Generic Hiking Group",
        description="We go on hiking trips, both local and further afield.",
        tags="hiking walking outdoors camping"
    )
    crafts = Group(
        name="Generic Crafts Group",
        description="We are a group that do various crafts together.",
        tags="craft crochet art textiles drawing"
    )
    tech = Group(
        name="Tech Social Group",
        description="A group for people who work with/in/around tech.",
        tags="tech programming code"
    )
    cycling = Group(
        name="Generic Cycling Group",
        description="We go on regular cycling trips to places.",
        tags="cycling outdoors sport fitness bike"
    )
    db.session.add_all([climbing, hiking, crafts, tech, cycling])

    start = now = datetime.now(tz=ZoneInfo('Europe/London')).replace(second=0, microsecond=0)

    for i in range(10):
        start_6pm = start.replace(hour=18, minute=0)
        start_7pm = start.replace(hour=19, minute=0)

        craft_event = Event(
            title="Craft social",
            description="Hang out, drink coffee and eat cake.",
            start=start_6pm,
            end=start_6pm+timedelta(hours=2),
            venue="Cool cafe",
            group=crafts
        )

        climb_event = Event(
            title="Bouldering event",
            description="Bouldering at a bouldering gym",
            start=start_7pm,
            end=start_7pm+timedelta(hours=3),
            venue="Bouldering gym",
            group=climbing
        )

        rope_event = Event(
            title="Rope climbing",
            description="Climbing some ropes really high",
            start=start_7pm+timedelta(days=2),
            end=start_7pm+timedelta(days=2, hours=3),
            venue="Rope climbing gym",
            group=climbing
        )

        db.session.add_all([craft_event, climb_event, rope_event])

        start += timedelta(days=7)

    start = now.replace(hour=12, minute=0) + timedelta(days=1)
    multi_day_event = Event(
        title="Camping trip",
        description="Camping over several days",
        start=start,
        end=start + timedelta(days=3),
        venue="In a forest",
        group=hiking
    )
    db.session.add(multi_day_event)

    start = now + timedelta(days=4)
    for i in range(10):
        start_1030am = start.replace(hour=10, minute=30)
        cycling_event = Event(
            title="Cycle to place",
            description="Cycle to a place far away and then back again.",
            start=start_1030am,
            venue="Some meeting point",
            group=cycling
        )

        start += timedelta(days=14)

        db.session.add(cycling_event)


    db.session.commit()
