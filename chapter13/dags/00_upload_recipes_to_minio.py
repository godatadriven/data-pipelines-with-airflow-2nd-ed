from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

with DAG(
    dag_id="00_upload_recipes_to_minio",
    schedule="@daily",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 7),
):
    upload_recipes_to_minio = DockerOperator(
        task_id="upload_recipes_to_minio",
        command="upload {{data_interval_start | ds}}",
        image="vectorvault_cli:latest",
        docker_url="tcp://docker-socket-proxy:2375",
        network_mode="chapter13_default",
        environment={
                "AWS_ENDPOINT_URL_S3":"{{ conn.minio.extra_dejson.get('endpoint_url') }}",
                "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
                "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
        },
        auto_remove=True,
        tty=True,
    )

