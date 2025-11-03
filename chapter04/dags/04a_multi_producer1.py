import datetime
from pathlib import Path

import pandas as pd
import pendulum
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, Asset, Metadata
from airflow.timetables.interval import CronDataIntervalTimetable

events_dataset = Asset("file:///data/events_04_1")


def _fetch_events(start_date, end_date, output_path, logical_date: datetime.datetime):
    Path(output_path).parent.mkdir(exist_ok=True, parents=True)

    events = pd.read_json(f"http://events-api:8081/events/range?start_date={start_date}&end_date={end_date}")
    events.to_json(output_path, orient="records", lines=True)

    yield Metadata(events_dataset, extra={"date": logical_date.strftime("%Y-%m-%d")})


with DAG(
    dag_id="04a_multi_producer1",
    start_date=pendulum.yesterday(),
    schedule=CronDataIntervalTimetable("0 0 * * *", timezone="UTC"),
    catchup=True,
):
    fetch_events = PythonOperator(
        task_id="fetch_events",
        python_callable=_fetch_events,
        op_kwargs={
            "start_date": "{{ data_interval_start | ds }}",
            "end_date": "{{ data_interval_end | ds }}",
            "output_path": "/data/events_04_1/{{ data_interval_start | ds }}.json",
        },
        outlets=[events_dataset],
    )
