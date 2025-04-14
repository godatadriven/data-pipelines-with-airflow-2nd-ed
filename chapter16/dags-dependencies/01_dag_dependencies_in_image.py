"""DAG demonstrating the umbrella use case with empty operators."""

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator


def _tf_version():
    import tensorflow as tf
    print("TensorFlow version:", tf.__version__)

with DAG(
    dag_id="01_dag_dependencies_in_image",
    description="Dag dependencies in custom image example.",
    start_date=pendulum.today("UTC").add(days=-5),
    schedule="@daily",
):
    some_init_task = EmptyOperator(task_id="init")
    version = PythonOperator(task_id="version", python_callable=_tf_version)
    finish = EmptyOperator(task_id="finish")

    # Set dependencies between all tasks
    some_init_task >> version >> finish
