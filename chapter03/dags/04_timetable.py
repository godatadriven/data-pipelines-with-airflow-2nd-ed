from pathlib import Path

import pandas as pd

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.timetables.events import EventsTimetable
import pendulum


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path, convert_dates=["timestamp"])

    stats = (events
             .assign(date=lambda df: df["timestamp"].dt.date)
             .groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


scheduled_launches = EventsTimetable(
    event_dates=[
        pendulum.datetime(year=2024, month=1, day=3),
        pendulum.datetime(year=2024, month=1, day=4),
        pendulum.datetime(year=2024, month=1, day=7)
    ]
)

with DAG(
    dag_id="04_timetable",
    schedule=scheduled_launches,
    start_date=pendulum.datetime(year=2024, month=1, day=1),
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=lambda **context: print(context["data_interval_start"], context["data_interval_end"]),
    )

    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/04_timetable/events && "
            "curl -o /data/04_timetable/events/{{ ds }}.json"
            " http://events-api:8081/events/latest"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/04_timetable/events/{{ ds }}.json",
            "output_path": "/data/04_timetable/stats/{{ ds }}.csv",
        },
    )

    print_context >> fetch_events >> calculate_stats
