from datetime import datetime
from pathlib import Path

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

from dotenv import load_dotenv
import os

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


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

DOCKER_URL =  "tcp://docker-socket-proxy:2375"

WEAVIATE_CONN_ID = "weaviate_default"
COLLECTION_NAME = "recipes"

common_dag_args = {
    "image":"gastrodb_cli:latest",
    "docker_url":DOCKER_URL,
    "network_mode":"chapter13_default",
    "environment":ENVIRONMENT,
    "auto_remove":"success",
    "tty":True,
}

with DAG(
    dag_id="vector_ingestion",
    schedule="@daily",
    start_date=datetime(2024, 10, 1),
    end_date=datetime(2024, 10, 8),
):
    upload_recipes_to_minio = DockerOperator(
        task_id="upload_recipes_to_minio",
        command="upload {{data_interval_start | ds}}",
        **common_dag_args
    )

    preprocess_recipes = DockerOperator(
        task_id="preprocess_recipes",
        command=[
            "preprocess",
            "s3://data/{{data_interval_start | ds}}",
        ],
        **common_dag_args
    )

    create_collection = DockerOperator(
        task_id="create_collection",
        command=f"create {COLLECTION_NAME} text-embedding-3-large",
        **common_dag_args
    )

    compare_db_documents = DockerOperator(
        task_id="compare_db_documents",
        command=[
            "compare",
            "s3://data/{{data_interval_start | ds}}",
            COLLECTION_NAME,
        ],
        **common_dag_args
    )

    delete_old_documents = DockerOperator(
        task_id="delete_old_documents",
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
        upload_recipes_to_minio >> 
        preprocess_recipes >> 
        create_collection >> 
        compare_db_documents >>
        delete_old_documents >>
        save_in_vectordb
    )