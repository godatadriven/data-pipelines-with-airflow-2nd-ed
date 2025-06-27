"""DAG demonstrating the umbrella use case with empty operators."""

import pendulum
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.sdk import DAG
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="02_teamA_dag_from_pvc",
    description="Dag persistence in PVC example.",
    start_date=pendulum.today("UTC").add(days=-5),
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
):
    teamA_init = EmptyOperator(task_id="teamA_init")

    echo_some = BashOperator(
        task_id="echo_some",
        bash_command='echo "Hello teamA from $(hostname)"',  # noqa: E501
    )

    # Set dependencies between all tasks
    teamA_init >> echo_some
