import datetime

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

dag1 = DAG(
    dag_id="figure_6_20_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
)
dag2 = DAG(
    dag_id="figure_6_20_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 18 * * *",
)

EmptyOperator(task_id="copy_to_raw", dag=dag1) >> EmptyOperator(task_id="process_supermarket", dag=dag1)

wait = ExternalTaskSensor(
    task_id="wait_for_process_supermarket",
    external_dag_id="figure_6_20_dag_1",
    external_task_id="process_supermarket",
    execution_delta=datetime.timedelta(hours=6),
    dag=dag2,
)
report = EmptyOperator(task_id="report", dag=dag2)
wait >> report
