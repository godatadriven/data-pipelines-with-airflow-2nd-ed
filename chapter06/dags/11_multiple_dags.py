from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.sensors.python import PythonSensor


def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()


with DAG(
    dag_id="11_ingest_supermarket_data",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
):

    for supermarket_id in range(1, 5):
        wait = PythonSensor(
            task_id=f"wait_for_supermarket_{supermarket_id}",
            python_callable=_wait_for_supermarket,
            op_kwargs={"supermarket_id_": f"supermarket{supermarket_id}"},
        )
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        trigger_create_metrics_dag = TriggerDagRunOperator(
            task_id=f"trigger_create_metrics_dag_supermarket_{supermarket_id}",
            trigger_dag_id="11_create_metrics",
        )
        wait >> copy >> process >> trigger_create_metrics_dag

with DAG(
    dag_id="11_create_metrics",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    compute_differences = EmptyOperator(task_id="compute_differences")
    update_dashboard = EmptyOperator(task_id="update_dashboard")
    notify_new_data = EmptyOperator(task_id="notify_new_data")
    compute_differences >> update_dashboard
