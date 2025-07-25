import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="hello_airflow",
    start_date=pendulum.today("UTC").add(days=-3),
    max_active_runs=1,
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
):

    print_hello = BashOperator(task_id="print_hello", bash_command="echo 'hello'")
    print_airflow = PythonOperator(
        task_id="print_airflow", python_callable=lambda: print("airflow")
    )

print_hello >> print_airflow
