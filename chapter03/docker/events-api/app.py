from datetime import date, timedelta
import itertools
import time

from faker import Faker
from fastapi import FastAPI
import numpy as np
import pandas as pd

app = FastAPI()


def _generate_events_daily(event_date: date):
    """Generates events for a given date."""

    # Use date as seed.
    seed = int(time.mktime(event_date.timetuple()))

    Faker.seed(seed)
    random_state = np.random.RandomState(seed)

    # Determine how many users and how many events we will have.
    n_users = random_state.randint(low=50, high=100)
    n_events = random_state.randint(low=200, high=1000)

    # Generate a bunch of users.
    fake = Faker()
    users = [fake.ipv4() for _ in range(n_users)]

    # Generate events for each user.
    events = pd.DataFrame(
        {
            "user": random_state.choice(users, size=n_events, replace=True),
            "timestamp": _random_datetimes(event_date, size=n_events, random_state=random_state),
        }
    ).sort_values(by="timestamp")

    # Convert events to records.
    records = events.to_dict(orient="records")

    return records


def _random_datetimes(event_date: date, size: int, random_state):
    """Generates a column of random datetimes on the given date."""
    return pd.to_timedelta(random_state.rand(size), unit='D') + pd.to_datetime(event_date)


def _generate_events_range(start_date: date, end_date: date):
    """Generates events for a range of dates (up to the end date, exclusive)."""
    return list(
        itertools.chain.from_iterable(
            _generate_events_daily(d)
            for d in date_range(start_date, end_date)
        )
    )


def date_range(start_date: date, end_date: date):
    """Iterator for a range of dates between start and end date (exclusive)."""
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/events/latest")
def events_latest():
    """Endpoint that returns events for the past 7 days."""
    start_date = date.today() - timedelta(days=7)
    end_date = date.today()
    return _generate_events_range(start_date, end_date)


@app.get("/events/range")
def events_range(start_date: date, end_date: date):
    """Endpoint that returns events between the given start and end dates (exclusive)."""
    return _generate_events_range(start_date, end_date)
