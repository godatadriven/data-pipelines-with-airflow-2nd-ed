import pendulum
from airflow.models import DAG
from airflow.operators.bash import BashOperator


def send_error(x):
    print("THE DAG ERRORED!")


dag = DAG(
    dag_id="04_task_failure_callback",
    default_args={"on_failure_callback": send_error},
    on_failure_callback=send_error,
    schedule=None,
    start_date=pendulum.today("UTC").add(days=-3),
)

failing_task = BashOperator(task_id="failing_task", bash_command="exit 1", dag=dag)
