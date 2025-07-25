"""
    Listing: 6.12
"""


import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable

def print_conf(**context):
    print(context["dag_run"].conf)
        
with DAG(
    dag_id="11_inspect_dag_run_config",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC")
):

    copy_to_raw = PythonOperator(task_id="copy_to_raw", python_callable=print_conf)
    process = PythonOperator(task_id="process", python_callable=print_conf)
    create_metrics = PythonOperator(task_id="create_metrics", python_callable=print_conf)
    copy_to_raw >> process >> create_metrics


