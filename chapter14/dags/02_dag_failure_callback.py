import pendulum
from airflow.sdk import DAG


def send_error():
    print("ERROR!")


dag = DAG(
    dag_id="02_dag_failure_callback",
    on_failure_callback=send_error,
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-3),
)
