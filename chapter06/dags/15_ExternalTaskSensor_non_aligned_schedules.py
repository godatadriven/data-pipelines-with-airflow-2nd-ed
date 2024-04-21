import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.sensors.external_task import ExternalTaskSensor

with DAG(dag_id = "dag1", schedule="0 16 * * *", start_date=pendulum.today("UTC").add(days=-3)):
    EmptyOperator(task_id="etl") 


with DAG(dag_id='15_ExternalTaskSensor_non_aligned_schedules',schedule="0 20 * * *", start_date=pendulum.today("UTC").add(days=-3)):
    wait = ExternalTaskSensor(
        task_id="wait_for_etl",
        external_dag_id="dag1",
        external_task_id="etl",
        )

