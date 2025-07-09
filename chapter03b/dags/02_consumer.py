from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset
from airflow.sdk.execution_time.comms import AssetEventDagRunReferenceResult
from airflow.sdk.execution_time.context import TriggeringAssetEventsAccessor

events_dataset = Asset("/data/events")


def _calculate_stats(input_path, output_path):
    """Calculates event statistics."""
    events = pd.read_json(input_path, convert_dates=["timestamp"], lines=True)

    stats = (
        events.assign(date=lambda df: df["timestamp"].dt.date).groupby(["date", "user"]).size().reset_index()
    )

    Path(output_path).parent.mkdir(exist_ok=True)
    stats.to_csv(output_path, index=False)


def _print_context(triggering_asset_events: TriggeringAssetEventsAccessor, **context):
    print(len(triggering_asset_events[events_dataset]))
    print(triggering_asset_events[events_dataset])
    result: AssetEventDagRunReferenceResult = triggering_asset_events[events_dataset][0]

    print(result.source_task_instance)
    print(result.extra)
    result.source_run_id
    result.source_dag_id

    print(context)

    # for asset, asset_events in triggering_asset_events.items():
    #     print(f"Asset: {asset.uri}")
    #     for event in asset_events:
    #         print(f"  - Triggered by DAG run: {event.source_dag_run.dag_id}")
    #         print(
    #             f"    Data interval: {event.source_dag_run.data_interval_start} to {event.source_dag_run.data_interval_end}"
    #         )
    #         print(f"    Run ID: {event.source_dag_run.run_id}")
    #         print(f"    Timestamp: {event.timestamp}")


with DAG(
    dag_id="02_consumer",
    schedule=[events_dataset],
    start_date=pendulum.datetime(year=2024, month=1, day=1),
):
    calculate_stats = PythonOperator(
        task_id="calculate_stats",
        python_callable=_print_context,
        # python_callable=_calculate_stats,
        # op_kwargs={
        #     "input_path": "/data/events/{{ (triggering_asset_events.values() | first | first).source_dag_run.data_interval_start }}.json",
        #     "output_path": "/data/stats/{{ (triggering_asset_events.values() | first | first).source_dag_run.data_interval_start }}.csv",
        # },
    )
