import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable


def _print_context(**context):
    print(context)

with DAG(
    dag_id="03_print_context_with_intent",
    start_date=pendulum.today("UTC").add(days=-15),
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
    catchup=True
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )
