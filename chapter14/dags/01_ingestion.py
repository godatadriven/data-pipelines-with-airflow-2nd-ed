from pathlib import Path
import pendulum

from airflow.sdk import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.timetables.trigger import CronTriggerTimetable

ENVIRONMENT = {
    "AWS_ENDPOINT_URL_S3": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
    "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
    "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
    "OPENAI_API_KEY": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('OPENAI_API_KEY') }}", 
    "AZURE_OPENAI_ENDPOINT": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_OPENAI_ENDPOINT') }}",
    "AZURE_OPENAI_RESOURCE_NAME": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_OPENAI_RESOURCE_NAME') }}",
    "WEAVIATE_HOST_PORT_REST": "{{ conn.weaviate_default.port }}",
    "WEAVIATE_HOST_PORT_GRPC": "{{ conn.weaviate_default.extra_dejson.get('grpc_port') }}",
    "OPENAI_CONN_TYPE":  "{{ conn.weaviate_default.extra_dejson.get('OPENAI_CONN_TYPE') }}"
}

COLLECTION_NAME = "recipes"

common_dag_args = {
    "image":"vectorvault_cli:latest",
    "docker_url":"tcp://docker-socket-proxy:2375",
    "network_mode":"chapter14_default",
    "environment":ENVIRONMENT,
    "auto_remove":"success",
    "tty":True,
}

with DAG(
    dag_id="01_Ingestion",
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
    start_date=pendulum.today("UTC"),
):
    preprocess_recipes = DockerOperator(
        task_id="preprocess_recipes",
        command=[
            "preprocess",
            "s3://data/{{data_interval_start | ds}}",
        ],
        trigger_rule="all_done",
        **common_dag_args
    )

    create_collection = DockerOperator(
        task_id="create_collection",
        command=f"create {COLLECTION_NAME} text-embedding-3-large",
        **common_dag_args
    )

    compare_objects = DockerOperator(
        task_id="compare_objects",
        command=[
            "compare",
            "s3://data/{{data_interval_start | ds}}",
            COLLECTION_NAME,
        ],
        **common_dag_args
    )

    delete_outdated_objects = DockerOperator(
        task_id="delete_outdated_objects",
        command=[
            "delete",
            "s3://data/{{data_interval_start | ds}}",
            COLLECTION_NAME,
        ],
         **common_dag_args
    )

    save_in_vectordb = DockerOperator(
        task_id="save_recipes_to_weaviate",
        command=[
            "save",
            COLLECTION_NAME,
            "s3://data/{{data_interval_start | ds}}",
        ],
        **common_dag_args
    )

    (
        preprocess_recipes >> 
        create_collection >> 
        compare_objects >>
        delete_outdated_objects >>
        save_in_vectordb
    )