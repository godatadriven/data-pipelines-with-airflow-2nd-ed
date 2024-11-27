"""
    Figure: 6.19
"""

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

with DAG(
    dag_id="13_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="extract")

with DAG(
    dag_id="13_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="extract")


with DAG(
    dag_id="13_dag_3",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="extract")

with DAG(
    dag_id="13_dag_4",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    [
        ExternalTaskSensor(
            task_id="wait_for_extract_dag1",
            external_dag_id="13_dag_1",
            external_task_id="extract",
        ),
        ExternalTaskSensor(
            task_id="wait_for_extract_dag2",
            external_dag_id="13_dag_2",
            external_task_id="extract",
        ),
        ExternalTaskSensor(
            task_id="wait_for_extract_dag3",
            external_dag_id="13_dag_3",
            external_task_id="extract",
        ),
    ] >> PythonOperator(task_id="data_science", python_callable=lambda: print("hello"))
