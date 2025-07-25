"""
    Listing: 6.10, 6.11
"""


import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="09_without_dag_run_configuration",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
    default_args={"depends_on_past": True},
):
    for supermarket_id in range(1, 5):
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        create_metrics = EmptyOperator(task_id=f"create_metrics_{supermarket_id}")
        copy >> process >> create_metrics