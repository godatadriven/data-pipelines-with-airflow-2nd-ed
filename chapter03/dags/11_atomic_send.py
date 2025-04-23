from pathlib import Path

import pandas as pd
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from pendulum import datetime


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""
    events = pd.read_json(input_path, convert_dates=["timestamp"])

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


def email_stats(stats, email):
    """Send an email..."""
    print(f"Sending stats to {email}...{stats}")


def _send_stats(email, stats_path):
    stats = pd.read_csv(stats_path)
    email_stats(stats, email=email)


with DAG(
    dag_id="11_atomic_send",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 5),
):
    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command=(
            "mkdir -p /data/11_atomic_send/events && "
            "curl -o /data/11_atomic_send/events/{{data_interval_start | ds}}.json "
            "'http://events-api:8081/events/range?"
            "start_date={{data_interval_start | ds}}&"
            "end_date={{data_interval_end | ds}}'"
        ),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/11_atomic_send/events/{{data_interval_start | ds}}.json",
            "output_path": "/data/11_atomic_send/stats/{{data_interval_start | ds}}.csv",
        },
    )

    send_stats = PythonOperator(
        task_id="send_stats",
        python_callable=_send_stats,
        op_kwargs={
            "email": "user@example.com",
            "stats_path": "/data/11_atomic_send/stats/{{data_interval_start | ds}}.csv",
        },
    )

    fetch_events >> calculate_stats >> send_stats
