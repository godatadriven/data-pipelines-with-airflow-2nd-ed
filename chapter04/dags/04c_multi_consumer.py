from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset

events_dataset_1 = Asset("file:///data/events_04_1")
events_dataset_2 = Asset("file:///data/events_04_2")


def _get_event(triggering_asset_events, uri):
    return triggering_asset_events[Asset(uri)][0]


def _calculate_stats(input_paths, output_path):
    """Calculates event statistics."""
    events = pd.concat(
        pd.read_json(input_path, convert_dates=["timestamp"], lines=True) for input_path in input_paths
    )

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


with DAG(
    dag_id="04c_multi_consumer",
    schedule=[events_dataset_1, events_dataset_2],
    start_date=pendulum.yesterday(),
    user_defined_macros={"get_event": _get_event},
):
    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_calculate_stats,
        op_kwargs={
            "input_paths": [
                "/data/events_04_1/{{ get_event(triggering_asset_events, 'file:///data/events_04_1').extra.date }}.json",
                "/data/events_04_2/{{ get_event(triggering_asset_events, 'file:///data/events_04_2').extra.date }}.json",
            ],
            "output_path": "/data/stats_04/{{ get_event(triggering_asset_events, 'file:///data/events_04_1').extra.date }}.csv",
        },
    )
