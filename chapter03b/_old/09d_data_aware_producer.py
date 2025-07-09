from pathlib import Path

import pandas as pd
import pendulum
from airflow.exceptions import AirflowSkipException
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset

events_dataset = Asset("/data/events")


def _fetch_events(start_date, end_date, output_path):
    if Path(output_path).exists():
        raise AirflowSkipException()
    else:
        Path(output_path).parent.mkdir(exist_ok=True, parents=True)
        events = pd.read_json(
            f"http://events-api:8081/events/range?start_date={start_date}&end_date={end_date}"
        )
        events.to_json(output_path, orient="records", lines=True)


with DAG(
    dag_id="09d_data_aware_producer",
    schedule="@daily",
    start_date=pendulum.datetime(year=2024, month=1, day=1),
    end_date=pendulum.datetime(year=2024, month=1, day=5),
):
    fetch_events = PythonOperator(
        task_id="fetch_events",
        python_callable=_fetch_events,
        op_kwargs={
            "start_date": "{{ data_interval_start | ds }}",
            "end_date": "{{ data_interval_end | ds }}",
            "output_path": "/data/events/{{ data_interval_start | ds }}.json",
        },
        outlets=[events_dataset],
    )
