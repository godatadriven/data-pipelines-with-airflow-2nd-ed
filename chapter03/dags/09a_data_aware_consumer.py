from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.python import PythonOperator
import pendulum


events_dataset = Dataset("/data/09_data_aware/events")


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""
    events = pd.read_json(input_path, convert_dates=["timestamp"], lines=True)

    stats = (events
             .assign(date=lambda df: df["timestamp"].dt.date)
             .groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="09a_data_aware_consumer",
    schedule=[events_dataset],
    start_date=pendulum.datetime(year=2024, month=1, day=1)
):
    def _print_context(**context):
        print(f'dataset_events: {list(context["triggering_dataset_events"].values())[0][0].source_dag_run.logical_date }')


    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )

    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/09_data_aware/events/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.json",
            "output_path": "/data/09_data_aware/stats/{{ (triggering_dataset_events.values() | first | first).source_dag_run.data_interval_start | ds }}.csv",
        },
    )

    print_context >> calculate_stats
