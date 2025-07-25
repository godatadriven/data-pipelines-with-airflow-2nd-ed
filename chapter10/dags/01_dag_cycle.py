import pendulum
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG

with DAG(
    dag_id="01_dag_cycle",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):
    t1 = EmptyOperator(task_id="t1")
    t2 = EmptyOperator(task_id="t2")
    t3 = EmptyOperator(task_id="t3")

    t1 >> t2 >> t3 >> t1
