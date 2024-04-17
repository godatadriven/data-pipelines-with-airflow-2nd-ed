from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator
import pendulum


events_dataset = Dataset("events")


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""

    print(input_path)

    events = pd.read_json(input_path, lines=True, convert_dates=["timestamp"])

    stats = (events
             .assign(date=lambda df: df["timestamp"].dt.date)
             .groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="xx_data_aware_consumer",
    schedule=[events_dataset],
    start_date=pendulum.datetime(year=2024, month=1, day=1)
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=lambda **context: print(context),
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/xx_data_aware/events/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.json",
            "output_path": "/data/xx_data_aware/stats/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.csv",
        },
    )

    print_context >> calculate_stats
