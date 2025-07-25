"""
    Figure: 6.7, 6.8
"""

import pendulum
from datetime import timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.sensors.filesystem import FileSensor
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="06_Sensor_deadlock",
    start_date=pendulum.today("UTC").add(days=-14),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="Create a file /data/supermarket1/data.csv, and behold a sensor deadlock.",
    catchup=True
):
    create_metrics = EmptyOperator(task_id="create_metrics")
    for supermarket_id in [1, 2, 3, 4]:
        copy = FileSensor(
            task_id=f"copy_to_raw_supermarket_{supermarket_id}",
            filepath=f"/data/supermarket{supermarket_id}/data.csv",
            timeout=600,
            execution_timeout=timedelta(seconds=60),
        )
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        copy >> process >> create_metrics
