from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator
import pendulum


events_dataset_09c = Dataset("/data/09_data_aware/events/09c")
events_dataset_09d = Dataset("/data/09_data_aware/events/09d")


def _calculate_stats(input_paths, output_path):
    """Calculates event statistics."""
    events = pd.concat([pd.read_json(path, convert_dates=["timestamp"], lines=True) for path in input_paths])

    stats = (events
             .assign(date=lambda df: df["timestamp"].dt.date)
             .groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="09e_data_aware_consumer",
    schedule=[events_dataset_09c,
              events_dataset_09d],
    start_date=pendulum.datetime(year=2024, month=1, day=1)
):
    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_paths": ["/data/09_data_aware/events/09c/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.json",
                            "/data/09_data_aware/events/09d/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.json"],
            "output_path": "/data/09_data_aware/stats/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.csv",
        },
    )

    calculate_stats
