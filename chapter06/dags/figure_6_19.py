import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.sensors.external_task import ExternalTaskSensor

dag1 = DAG(
    dag_id="figure_6_19_dag_1",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
)
dag2 = DAG(
    dag_id="figure_6_19_dag_2",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
)
dag3 = DAG(
    dag_id="figure_6_19_dag_3",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 0 * * *",
)
dag4 = DAG(
    dag_id="figure_6_19_dag_4",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
)

EmptyOperator(task_id="etl", dag=dag1)
EmptyOperator(task_id="etl", dag=dag2)
EmptyOperator(task_id="etl", dag=dag3)
[
    ExternalTaskSensor(
        task_id="wait_for_etl_dag1",
        external_dag_id="figure_6_19_dag_1",
        external_task_id="etl",
        dag=dag4,
    ),
    ExternalTaskSensor(
        task_id="wait_for_etl_dag2",
        external_dag_id="figure_6_19_dag_2",
        external_task_id="etl",
        dag=dag4,
    ),
    ExternalTaskSensor(
        task_id="wait_for_etl_dag3",
        external_dag_id="figure_6_19_dag_3",
        external_task_id="etl",
        dag=dag4,
    ),
] >> PythonOperator(task_id="report", dag=dag4, python_callable=lambda: print("hello"))
