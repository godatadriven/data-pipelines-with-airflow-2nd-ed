"""
    Listing: 6.7
"""

from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

with DAG(dag_id="16_upstream_dag", schedule="0 16 * * *", start_date=pendulum.today("UTC").add(days=-3)):
    EmptyOperator(task_id="etl")


with DAG(
    dag_id="16_ExternalTaskSensor_schedule_offset",
    schedule="0 20 * * *",
    start_date=pendulum.today("UTC").add(days=-3),
):
    wait = ExternalTaskSensor(
        task_id="wait_for_etl",
        external_dag_id="16_upstream_dag",
        external_task_id="etl",
        execution_delta=timedelta(hours=4),
    )
