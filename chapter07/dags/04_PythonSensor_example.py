"""
    Listing: 6.2
"""


from datetime import timedelta
from pathlib import Path

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.sensors.python import PythonSensor
from airflow.timetables.trigger import CronTriggerTimetable


def _wait_for_supermarket(supermarket_id_):
    supermarket_path = Path("/data/" + supermarket_id_)
    data_files = supermarket_path.glob("data-*.csv")
    success_file = supermarket_path / "_SUCCESS"
    return data_files and success_file.exists()


with DAG(
    dag_id="04_PythonSensor_example",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
    description="A batch workflow for ingesting supermarket promotions data.",
    default_args={"depends_on_past": True},
):
    wait_for_supermarket_1 = PythonSensor(
        task_id="wait_for_supermarket_1",
        python_callable=_wait_for_supermarket,
        op_kwargs={"supermarket_id_": "supermarket1"},
        timeout=timedelta(minutes=5),
    )
