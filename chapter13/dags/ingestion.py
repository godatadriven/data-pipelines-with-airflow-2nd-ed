from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from dotenv import load_dotenv
import os


ENVIRONMENT = {
    "AWS_ENDPOINT_URL_S3": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
    "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
    "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
    "AZURE_OPENAI_API_KEY": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_OPENAI_API_KEY') }}", 
    "AZURE_OPENAI_ENDPOINT": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_OPENAI_ENDPOINT') }}",
    "AZURE_OPENAI_RESOURCE_NAME": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_OPENAI_RESOURCE_NAME') }}",
    "WEAVIATE_HOST_PORT_REST": "{{ conn.weaviate_default.port }}",
    "WEAVIATE_HOST_PORT_GRPC": "{{ conn.weaviate_default.extra_dejson.get('grpc_port') }}",
}

DOCKER_URL =  "tcp://docker-socket-proxy:2375"

WEAVIATE_CONN_ID = "weaviate_default"
COLLECTION_NAME = "recipes"

with DAG(
    dag_id="vector_ingestion",
    schedule="@daily",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 8),
):
    # Check network with docker network ls        
    # name of the source folder + _default
    upload_recipes_to_minio = DockerOperator(
        task_id="upload_recipes_to_minio",
        docker_url=DOCKER_URL,
        image="gastrodb_cli:latest",
        command=[
            "upload",
            "{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    preprocess_recipes = DockerOperator(
        task_id="preprocess_recipes",
        docker_url=DOCKER_URL,
        image="gastrodb_cli:latest",
        command=[
            "preprocess",
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    split_recipes_into_chunks = DockerOperator(
        task_id="split_recipes_into_chunks",
        docker_url=DOCKER_URL,
        image="gastrodb_cli:latest",
        command=[
            "split",
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    create_collection = DockerOperator(
        task_id="create_collection",
        docker_url=DOCKER_URL,
        image="gastrodb_cli:latest",
        command=[
            "create",
            COLLECTION_NAME,
            "text-embedding-3-large",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT,
    )


    save_in_vectordb = DockerOperator(
        task_id="save_recipes_to_weaviate",
        docker_url=DOCKER_URL,
        image="gastrodb_cli:latest",
        command=[
            "save",
            COLLECTION_NAME,
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT,
    )

    (
        upload_recipes_to_minio >> 
        preprocess_recipes >> 
        split_recipes_into_chunks >>  
        create_collection >> 
        save_in_vectordb
    )