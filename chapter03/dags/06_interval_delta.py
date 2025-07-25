from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path, convert_dates=["timestamp"])

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="06_interval_delta",
    schedule=CronDataIntervalTimetable("@daily", timezone="UTC"),
    start_date=pendulum.datetime(year=2024, month=1, day=1, tz="Europe/Amsterdam"),
    end_date=pendulum.datetime(year=2024, month=1, day=5),
    catchup=True,
):
    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/06_interval_delta/events/ && "
            "curl -o /data/06_interval_delta/events/{{ logical_date | ds }}.json "
            "'http://events-api:8081/events/range?"
            "start_date={{ data_interval_start | ds }}&end_date={{ data_interval_end | ds }}'"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/06_interval_delta/events/{{ logical_date | ds }}.json",
            "output_path": "/data/06_interval_delta/stats/{{ logical_date | ds }}.csv",
        },
    )

    fetch_events >> calculate_stats
