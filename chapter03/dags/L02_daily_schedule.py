from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    events = pd.read_json(input_path)
    stats = events.groupby(["date", "user"]).size().reset_index()

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="L02_daily_schedule",
    schedule="@daily",
    start_date=datetime(2024, 1, 1),
):
    fetch_events = BashOperator(
        task_id="fetch_events",
        bash_command="curl -o /data/events.json http://events_api:5000/events",
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/events.json",
            "output_path": "/data/stats.csv",
        },
    )

    fetch_events >> calculate_stats
