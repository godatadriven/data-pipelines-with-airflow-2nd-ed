import datetime as dt

from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator


with DAG(
    dag_id="01_docker",
    description="Fetches ratings from the Movielens API using Docker.",
    start_date=dt.datetime(2019, 1, 1),
    end_date=dt.datetime(2019, 1, 1),
    schedule_interval="@daily",
) as dag:

    environment= {
        "MLFLOW_TRACKING_URI": "http://mlflow:9002",
        "MLFLOW_S3_ENDPOINT_URL": "http://minio:9000",
        "AWS_ENDPOINT_URL_S3": "http://minio:9000",
        "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
        "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}"
    }

    fetch_dataset = DockerOperator(
        task_id="fetch_dataset",
        image="jrderuiter/fashion-model",
        command=[
            "fetch",
            "s3://data/{{ds}}/train",
            "s3://data/{{ds}}/test",
        ],
        network_mode="chapterml_airflow",
        environment=environment
    )


    train_model = DockerOperator(
        task_id="train_model",
        image="jrderuiter/fashion-model",
        command=[
            "train",
            "s3://data/{{ds}}/train",
            "--epochs",
            "5"
        ],
        network_mode="chapterml_airflow",
        environment=environment
    )

    evaluate_model = DockerOperator(
        task_id="evaluate_model",
        image="jrderuiter/fashion-model",
        command=[
            "evaluate",
            "s3://data/{{ds}}/test",
            "{{ task_instance.xcom_pull(task_ids='train_model', key='return_value') }}"
        ],
        network_mode="chapterml_airflow",
        environment=environment
    )

    fetch_dataset >> train_model
    [fetch_dataset, train_model] >> evaluate_model
