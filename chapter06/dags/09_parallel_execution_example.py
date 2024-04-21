from pathlib import Path

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.python import PythonSensor



def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()


with DAG(
    dag_id="09_parallel_execution_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
    default_args={"depends_on_past": True},
):

    for supermarket_id in range(1, 5):
        wait = PythonSensor(
            task_id=f"wait_for_supermarket_{supermarket_id}",
            python_callable=_wait_for_supermarket,
            op_kwargs={"supermarket_id_": f"supermarket{supermarket_id}"},
            timeout=600,
        )

        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        create_metrics = EmptyOperator(task_id=f"create_metrics_{supermarket_id}")
        wait >> copy >> process >> create_metrics
