"""
    Listing: 6.1
"""

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="02_wait_for_supermarket_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the FileSensor.",
    default_args={"depends_on_past": True},
):
    wait_for_supermarket = FileSensor(
        task_id="wait_for_supermarket_1", filepath="/data/supermarket1/data.csv"
    )
