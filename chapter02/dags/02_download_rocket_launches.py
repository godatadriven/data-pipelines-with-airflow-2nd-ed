import pendulum
from airflow.sdk import DAG

with DAG(
    dag_id="02_download_rocket_launches",
    start_date=pendulum.today("UTC").add(days=-14),
    schedule=None,
):
    ...
