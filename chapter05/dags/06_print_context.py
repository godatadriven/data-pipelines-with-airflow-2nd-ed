from pprint import pprint

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable


def _print_context(**kwargs):
    print(kwargs)


with DAG(
    dag_id="06_print_context",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("@hourly", timezone="UTC"),
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )
