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
    EmptyOperator(task_id="etl")

with DAG(
    dag_id="13_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="etl")


with DAG(
    dag_id="13_dag_3",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
):
    EmptyOperator(task_id="etl")

with DAG(
    dag_id="13_dag_4",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    [
        ExternalTaskSensor(
            task_id="wait_for_etl_dag1",
            external_dag_id="13_dag_1",
            external_task_id="etl",
        ),
        ExternalTaskSensor(
            task_id="wait_for_etl_dag2",
            external_dag_id="13_dag_2",
            external_task_id="etl",
        ),
        ExternalTaskSensor(
            task_id="wait_for_etl_dag3",
            external_dag_id="13_dag_3",
            external_task_id="etl",
        ),
    ] >> PythonOperator(task_id="report", python_callable=lambda: print("hello"))
