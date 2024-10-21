import json
import os
from datetime import datetime
from pathlib import Path

from custom.operators import CreateWeaviateCollectionOperator
from airflow import DAG
from airflow.decorators import task
from airflow.models.baseoperator import chain
from airflow.providers.docker.operators.docker import DockerOperator

DOCKER_URL =  "tcp://docker-socket-proxy:2375"

ENVIRONMENT = {
    "AWS_ENDPOINT_URL_S3": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
    "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
    "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}",
    "AZURE_OPEN_API_KEY": "",
    "AZURE_OPEN_AI_ORGANIZATION":"",
    "AZURE_OPEN_AI_BASE_URL":"{{ conn.weaviate_default.host }}",
}


WEAVIATE_CONN_ID = "weaviate_default"
class_object_data = json.loads(Path("./dags/schema.json").read_text())["classes"][0]
CLASS_NAME = "Ismael2"
VECTORIZER = "text2vec-transformers"

class_object_data["class"] = CLASS_NAME
class_object_data["vectorizer"] = VECTORIZER


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
        network_mode="chapter13_genai_default",
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
        network_mode="chapter13_genai_default",
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
        network_mode="chapter13_genai_default",
        environment=ENVIRONMENT
    )

    create_class = CreateWeaviateCollectionOperator(
        task_id="create_class",
        conn_id=WEAVIATE_CONN_ID,
        collection_name="recipes",
    )



    # print_dict = PythonOperator(task_id="print_dict", python_callable=print_dict, trigger_rule="none_failed")

    # a = pd.read_parquet("./dags/astro_blog.parquet").to_dict(orient="records")[:3]

    # import_data = WeaviateIngestOperator(
    #     task_id="import_data",
    #     conn_id=WEAVIATE_CONN_ID,
    #     class_name=CLASS_NAME,
    #     input_json=a,
    #     trigger_rule="none_failed",
    # )

    (
        upload >> preprocess >> split >> create_class
         #>>  import_data
    )