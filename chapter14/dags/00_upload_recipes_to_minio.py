from datetime import datetime
from pathlib import Path
import pendulum

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="00_upload_recipes_to_minio",
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
    start_date=pendulum.today("UTC"),
):
    upload_recipes_to_minio = DockerOperator(
        task_id="upload_recipes_to_minio",
        command="upload {{data_interval_start | ds}}",
        image="vectorvault_cli:latest",
        network_mode="chapter14_default",
        environment={
                "AWS_ENDPOINT_URL_S3":"{{ conn.minio.extra_dejson.get('endpoint_url') }}",
                "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
                "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
        },
        auto_remove="success",
        tty=True,
    )

