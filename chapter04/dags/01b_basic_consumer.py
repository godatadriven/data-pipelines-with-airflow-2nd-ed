from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset

events_dataset = Asset("file:///data/events_01")


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""
    events = pd.read_json(input_path, convert_dates=["timestamp"], lines=True)

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="01b_basic_consumer",
    schedule=[events_dataset],
    start_date=pendulum.yesterday(),
):
    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_path": "/data/events_01/{{ (triggering_asset_events.values() | first | first).source_dag_run.logical_date }}.json",
            "output_path": "/data/stats_01/{{ (triggering_asset_events.values() | first | first).source_dag_run.logical_date }}.csv",
        },
    )
