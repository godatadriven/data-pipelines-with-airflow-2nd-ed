"""
    Figure: 6.5
"""


import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor

with DAG(
    dag_id="03_file_sensor_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the FileSensor.",
    default_args={"depends_on_past": True},
):
    create_metrics = EmptyOperator(task_id="create_metrics")

    for supermarket_id in [1, 2, 3, 4]:
        wait = FileSensor(
            task_id=f"wait_for_supermarket_{supermarket_id}",
            filepath=f"/data/supermarket{supermarket_id}/data.csv",
        )
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        wait >> copy >> process >> create_metrics
