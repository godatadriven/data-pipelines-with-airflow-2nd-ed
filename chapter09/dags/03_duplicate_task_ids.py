import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

dag = DAG(
    dag_id="chapter09_duplicate_task_ids",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
)

t1 = EmptyOperator(task_id="task", dag=dag)
for i in range(5):
    EmptyOperator(task_id="task", dag=dag) >> t1
