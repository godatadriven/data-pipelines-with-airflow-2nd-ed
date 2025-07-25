"""
    Listing: 6.3
"""

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="07_concurrency_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    max_active_tasks=50
):
    EmptyOperator(task_id="dummy")
