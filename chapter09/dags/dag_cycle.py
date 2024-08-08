import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

dag = DAG(
    dag_id="chapter8_dag_cycle",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
)

t1 = EmptyOperator(task_id="t1", dag=dag)
t2 = EmptyOperator(task_id="t2", dag=dag)
t3 = EmptyOperator(task_id="t3", dag=dag)

t1 >> t2 >> t3 >> t1
