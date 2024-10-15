import json
import os
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.decorators import task
from airflow.models.baseoperator import chain
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
# from airflow.providers.weaviate.operators.weaviate import WeaviateHook, WeaviateIngestOperator
from airflow.providers.docker.operators.docker import DockerOperator

DOCKER_URL =  "tcp://docker-socket-proxy:2375"


weaviate_conn_id = "weaviate_default"
class_object_data = json.loads(Path("./dags/schema.json").read_text())["classes"][0]
CLASS_NAME = "Ismael2"
VECTORIZER = "text2vec-transformers"

class_object_data["class"] = CLASS_NAME
class_object_data["vectorizer"] = VECTORIZER


with DAG(
    dag_id="ingestion",
    schedule="@daily",
    start_date=datetime.today() - timedelta(days=3),
):

    fetch_dataset = DockerOperator(
        task_id="fetch_dataset",
        docker_url=DOCKER_URL,
        image="recipe_book:latest",
        command=[
            "transfer",
            "s3://data/{{data_interval_start | ds}}/train",
            "s3://data/{{data_interval_start | ds}}/test",
        ],
        # network_mode="s3-transfer-service",
        # environment=environment
    )

    @task.branch
    def check_for_class() -> bool:
        "Check if the provided class already exists and decide on the next step."
        hook = WeaviateHook(weaviate_conn_id)
        client = hook.get_client()

        if not client.schema.get()["classes"]:
            print("No classes found in this weaviate instance.")
            return "create_class"

        existing_classes_names_with_vectorizer = [x["class"] for x in client.schema.get()["classes"]]

        print(f"Existing classes: {existing_classes_names_with_vectorizer}")

        if CLASS_NAME in existing_classes_names_with_vectorizer:
            print(f"Schema for class {CLASS_NAME} exists.")
            return "class_exists"
        else:
            print(f"Class {CLASS_NAME} does not exist yet.")
            return "create_class"

    @task
    def create_class():
        "Create a class with the provided name and vectorizer."
        weaviate_hook = WeaviateHook(weaviate_conn_id)

        class_obj = {
            "class": CLASS_NAME,
            "vectorizer": VECTORIZER,
        }
        weaviate_hook.create_class(class_obj)

    class_exists = EmptyOperator(task_id="class_exists")

    # print_dict = PythonOperator(task_id="print_dict", python_callable=print_dict, trigger_rule="none_failed")

    # a = pd.read_parquet("./dags/astro_blog.parquet").to_dict(orient="records")[:3]

    # import_data = WeaviateIngestOperator(
    #     task_id="import_data",
    #     conn_id=weaviate_conn_id,
    #     class_name=CLASS_NAME,
    #     input_json=a,
    #     trigger_rule="none_failed",
    # )

    fetch_dataset >> check_for_class() >> [create_class(), class_exists] #>>  import_data
