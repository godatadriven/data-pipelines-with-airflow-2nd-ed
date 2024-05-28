"""
    Listing: 6.1
"""

import pendulum
from airflow import DAG
from airflow.sensors.filesystem import FileSensor

with DAG(
    dag_id="02_wait_for_supermarket_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the FileSensor.",
    default_args={"depends_on_past": True},
):
    wait_for_supermarket = FileSensor(
        task_id="wait_for_supermarket_1", filepath="/data/supermarket1/data.csv"
    )
