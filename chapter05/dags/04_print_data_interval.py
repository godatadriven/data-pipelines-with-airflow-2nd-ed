import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.interval import CronDataIntervalTimetable


def _print_context(**context):
    start = context["data_interval_start"]
    end = context["data_interval_end"]
    print(f"Start: {start}, end: {end}")
    # Prints e.g.:
    # Start: 2024-07-13T14:00:00+00:00, end: 2024-07-13T15:00:00+00:00


with DAG(
    dag_id="04_print_data_interval",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronDataIntervalTimetable("@daily", "UTC"),
    catchup=True
):
    print_context = PythonOperator(
        task_id="print_context",
        python_callable=_print_context,
    )
