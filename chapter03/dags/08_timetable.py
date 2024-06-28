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

holiday_days = EventsTimetable(
    event_dates=[
        pendulum.datetime(2024, 1, 1),
        pendulum.datetime(2024, 3, 31),
        pendulum.datetime(2024, 5, 2),
    ],
)


pendulum
with DAG(
    dag_id="08_timetable",
    schedule=holiday_days,
    start_date=pendulum.datetime(year=2024, month=1, day=1),
):
    def _print_context(**context):
        print(f'Start: {context["data_interval_start"]}, End: {context["data_interval_end"]}')

    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )

    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/08_timetable/events && "
            "curl -o /data/08_timetable/events/{{ logical_date | ds }}.json"
            " http://events-api:8081/events/latest"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/08_timetable/events/{{ ds }}.json",
            "output_path": "/data/08_timetable/stats/{{ ds }}.csv",
        },
    )

    print_context >> fetch_events >> calculate_stats