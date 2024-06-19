from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime


def _calculate_stats(**context):
    """Calculates event statistics."""
    input_path = context["templates_dict"]["input_path"]
    output_path = context["templates_dict"]["output_path"]

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)

    _email_stats(stats, email="user@example.com")


def _email_stats(stats, email):
    """Send an email..."""
    print(f"Sending stats to {email}...")


with DAG(
    dag_id="10_non_atomic_send",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 5),
    catchup=True,
):
    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/10_non_atomic_send/events && "
            "curl -o /data/10_non_atomic_send/events/{{logical_date | ds}}.json "
            "http://events-api:8081/events/range?"
            "start_date={{data_interval_start | ds}}&"
            "end_date={{data_interval_end | ds}}"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        templates_dict={
            "input_path": "/data/10_non_atomic_send/events/{{logical_date | ds}}.json",
            "output_path": "/data/10_non_atomic_send/stats/{{logical_date | ds}}.csv",
        },
    )

    fetch_events >> calculate_stats
