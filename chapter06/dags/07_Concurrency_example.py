"""
    Listing: 6.3
"""

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="07_Concurrency_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="@daily",
    concurrency=50,
):
    EmptyOperator(task_id="dummy")
