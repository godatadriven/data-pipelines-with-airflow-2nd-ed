import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="testme",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    t1 = EmptyOperator(task_id="test")
    for tasknr in range(5):
        BashOperator(task_id="test2", bash_command=f"echo '{tasknr}'") >> t1
