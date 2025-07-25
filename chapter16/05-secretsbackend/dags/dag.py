import pendulum
from airflow.providers.http.operators.http import HttpOperator
from airflow.sdk import DAG

with DAG(
    dag_id="secretsbackend_with_vault",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=None,
):

    call_api = HttpOperator(
        task_id="call_api",
        http_conn_id="secure_api",
        method="GET",
        endpoint="",
        log_response=True,
    )
