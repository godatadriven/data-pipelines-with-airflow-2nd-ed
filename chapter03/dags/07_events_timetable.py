from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.events import EventsTimetable


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path, convert_dates=["timestamp"])

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


public_holidays = EventsTimetable(
    event_dates=[
        pendulum.datetime(year=2024, month=1, day=1),
        pendulum.datetime(2024, 3, 31),
        pendulum.datetime(2024, 5, 2),
    ],
    restrict_to_events=True,
)


with DAG(
    dag_id="07_events_timetable",
    schedule=public_holidays,
    start_date=pendulum.datetime(year=2024, month=1, day=1),
    catchup=True,
):
    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/07_events_timetable/events && "
            "curl -o /data/07_events_timetable/events/{{ logical_date | ds }}.json "
            "'http://events-api:8081/events/latest'"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/07_events_timetable/events/{{ logical_date | ds }}.json",
            "output_path": "/data/07_events_timetable/stats/{{ logical_date | ds }}.csv",
        },
    )

    fetch_events >> calculate_stats
