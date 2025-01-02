import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id="chapter09_bash_operator_no_command",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    BashOperator(task_id="this_should_fail")
