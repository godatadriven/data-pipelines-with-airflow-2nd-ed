import pendulum
from airflow.models import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

dag = DAG(
    dag_id="hello_world",
    start_date=pendulum.today("UTC").add(days=-3),
    max_active_runs=1,
    schedule_interval="@daily",
)

hello = BashOperator(task_id="hello", bash_command="echo 'hello'", dag=dag)
world = PythonOperator(task_id="world", python_callable=lambda: print("airflow"), dag=dag)

hello >> world
