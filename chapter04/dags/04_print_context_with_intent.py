import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def _print_context(**context):
    print(context)


with DAG(
    dag_id="04_print_context_with_intent",
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@daily",
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )
