import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def _print_context(**context):
    start = context["data_interval_start"]
    end = context["data_interval_end"]
    print(f"Start: {start}, end: {end}")
    # Prints e.g.:
    # Start: 2019-07-13T14:00:00+00:00, end: 2019-07-13T15:00:00+00:00


with DAG(
    dag_id="04_print_execution_date",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="@daily",
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )
