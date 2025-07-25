"""
    Figure: 6.1
"""

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="01_supermarket_promotions",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the FileSensor.",
    default_args={"depends_on_past": True},
):
    create_metrics = EmptyOperator(task_id="create_metrics")

    for supermarket_id in [1, 2, 3, 4]:
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        copy >> process >> create_metrics
