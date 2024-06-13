"""
    Listing: 6.5
    Figure: 6.20
"""

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

with DAG(
    dag_id="14_ingest_supermarket_data",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
):
    (EmptyOperator(task_id="copy_to_raw") >> EmptyOperator(task_id="process_supermarket"))

with DAG(
    dag_id="14_wait_for_process_supermarket",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
):
    wait = ExternalTaskSensor(
        task_id="wait_for_process_supermarket",
        external_dag_id="14_ingest_supermarket_data",
        external_task_id="process_supermarket",
    )
    report = EmptyOperator(task_id="report")
    wait >> report
