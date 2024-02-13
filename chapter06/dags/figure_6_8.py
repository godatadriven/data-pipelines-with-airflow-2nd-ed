import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.filesystem import FileSensor

with DAG(
    dag_id="figure_6_08",
    start_date=pendulum.today("UTC").add(days=-14),
    schedule="0 16 * * *",
    description="Create a file /data/supermarket1/data.csv, and behold a sensor deadlock.",
):
    create_metrics = EmptyOperator(task_id="create_metrics")
    for supermarket_id in [1, 2, 3, 4]:
        copy = FileSensor(
            task_id=f"copy_to_raw_supermarket_{supermarket_id}",
            filepath=f"/data/supermarket{supermarket_id}/data.csv",
        )
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        copy >> process >> create_metrics
