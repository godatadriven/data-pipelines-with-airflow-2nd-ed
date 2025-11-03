from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset
from airflow.timetables.interval import CronDataIntervalTimetable

events_dataset = Asset("file:///data/events_01", extra={"description": "My events dataset."})


def _fetch_events(start_date, end_date, output_path):
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)
    events = pd.read_json(f"http://events-api:8081/events/range?start_date={start_date}&end_date={end_date}")
    events.to_json(output_path, orient="records", lines=True)


with DAG(
    dag_id="01a_basic_producer",
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="UTC"),
    start_date=pendulum.yesterday(),
    catchup=True,
):
    fetch_events = PythonOperator(
        task_id="fetch_events",
        python_callable=_fetch_events,
        op_kwargs={
            "start_date": "{{ data_interval_start | ds }}",
            "end_date": "{{ data_interval_end | ds }}",
            "output_path": "/data/events_01/{{ data_interval_start | ds }}.json",
        },
        outlets=[events_dataset],
    )
