"""
    Figure: 6.6
"""


from pathlib import Path

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.sensors.python import PythonSensor
from airflow.timetables.trigger import CronTriggerTimetable


def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()


with DAG(
    dag_id="05_PythonSensor_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
    default_args={"depends_on_past": True},
):
    create_metrics = EmptyOperator(task_id="create_metrics")

    for supermarket_id in range(1, 5):
        wait = PythonSensor(
            task_id=f"wait_for_supermarket_{supermarket_id}",
            python_callable=_wait_for_supermarket,
            op_kwargs={"supermarket_id_": f"supermarket{supermarket_id}"},
            timeout=600,
        )
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        wait >> copy >> process >> create_metrics
