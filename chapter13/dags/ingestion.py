from datetime import datetime
from pathlib import Path

from custom.operators import WeaviateCreateCollectionOperator
from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator

DOCKER_URL =  "tcp://docker-socket-proxy:2375"


ENVIRONMENT = {
    "AWS_ENDPOINT_URL_S3": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
    "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
    "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
    "X-Azure-Api-Key": "{{ conn.weaviate_default.extra_dejson.get('additional_headers').get('AZURE_API_KEY') }}", 
    "WEAVIATE_HOST_PORT_REST": "{{ conn.weaviate_default.port }}",
    "WEAVIATE_HOST_PORT_GRPC": "{{ conn.weaviate_default.extra_dejson.get('grpc_port') }}",
}

WEAVIATE_CONN_ID = "weaviate_default"
COLLECTION_NAME = "recipes"

with DAG(
    dag_id="ingestion",
    schedule="@daily",
    start_date=datetime(2024, 10, 14),
    end_date=datetime(2024, 10, 16),
):
    # Check network with docker network ls        
    # name of the source folder + _default
    upload = DockerOperator(
        task_id="upload_recipes_to_minio",
        docker_url=DOCKER_URL,
        image="recipe_book:latest",
        command=[
            "upload",
            "/app/sample_recipes/{{data_interval_start | ds}}",
            "s3://data/{{data_interval_start | ds}}/raw",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    preprocess = DockerOperator(
        task_id="preprocess_recipes",
        docker_url=DOCKER_URL,
        image="recipe_book:latest",
        command=[
            "preprocess",
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    
    split = DockerOperator(
        task_id="split_recipes_into_chunks",
        docker_url=DOCKER_URL,
        image="recipe_book:latest",
        command=[
            "split",
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    create_collection = WeaviateCreateCollectionOperator(
        task_id="create_collection",
        conn_id=WEAVIATE_CONN_ID,
        collection_name=COLLECTION_NAME,
        name_of_configuration="recipe_vectorizer",
        metadata_fields=["filename", "description"],
        embedding_model="text-embedding-3-large",
    )

    save_in_vectordb = DockerOperator(
        task_id="save_recipes_to_weaviate",
        docker_url=DOCKER_URL,
        image="recipe_book:latest",
        command=[
            "save",
            COLLECTION_NAME,
            "s3://data/{{data_interval_start | ds}}",
        ],
        network_mode="chapter13_default",
        environment=ENVIRONMENT
    )

    (
        upload >> preprocess >> split >>  create_collection >> save_in_vectordb
    )