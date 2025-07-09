import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable

dag = DAG(
    dag_id="05_hello_world_on_edge",
    start_date=pendulum.today("UTC").add(days=-3),
    max_active_runs=1,
    schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC"),
)

hello = BashOperator(task_id="hello", bash_command="echo 'hello'", dag=dag, executor='airflow.providers.edge3.executors.EdgeExecutor')
world = PythonOperator(task_id="world", python_callable=lambda: print("airflow"), dag=dag)

hello >> world
