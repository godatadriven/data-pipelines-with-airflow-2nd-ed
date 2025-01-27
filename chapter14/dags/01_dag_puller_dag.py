import datetime

from airflow.models import DAG
from airflow.operators.bash import BashOperator

dag = DAG(
    dag_id="01_dag_puller_dag",
    default_args={"depends_on_past": False},
    start_date=datetime.datetime(2024, 1, 1),
    schedule=datetime.timedelta(minutes=5),
    catchup=False,
)

fetch_code = BashOperator(
    task_id="fetch_code",
    bash_command=(
        "cd /opt/airflow/dags && "
        "git reset --hard origin/master"  # NOTE: Git must be configured for this to work
    ),
    dag=dag,
)
