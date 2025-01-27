import pendulum
from airflow.models import DAG


def send_error():
    print("ERROR!")


dag = DAG(
    dag_id="03_dag_failure_callback",
    on_failure_callback=send_error,
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-3),
)
