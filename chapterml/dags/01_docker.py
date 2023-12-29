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

    docker_url = "tcp://docker-socket-proxy:2375"

    environment= {
        "MLFLOW_TRACKING_URI": "{{ conn.mlflow.get_uri() }}",
        "MLFLOW_S3_ENDPOINT_URL": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
        "AWS_ENDPOINT_URL_S3": "{{ conn.minio.extra_dejson.get('endpoint_url') }}",
        "AWS_ACCESS_KEY_ID": "{{ conn.minio.login }}",
        "AWS_SECRET_ACCESS_KEY": "{{ conn.minio.password }}"
    }

    fetch_dataset = DockerOperator(
        task_id="fetch_dataset",
        docker_url=docker_url,
        image="jrderuiter/fashion-model",
        command=[
            "fetch",
            "s3://data/{{ds}}/train",
            "s3://data/{{ds}}/test",
        ],
        network_mode="chapterml_default",
        environment=environment
    )

    train_model = DockerOperator(
        task_id="train_model",
        docker_url=docker_url,
        image="jrderuiter/fashion-model",
        command=[
            "train",
            "s3://data/{{ds}}/train",
            "--epochs",
            "5"
        ],
        network_mode="chapterml_default",
        environment=environment
    )

    evaluate_model = DockerOperator(
        task_id="evaluate_model",
        docker_url=docker_url,
        image="jrderuiter/fashion-model",
        command=[
            "evaluate",
            "s3://data/{{ds}}/test",
            "{{ task_instance.xcom_pull(task_ids='train_model', key='return_value') }}"
        ],
        network_mode="chapterml_default",
        environment=environment
    )

    fetch_dataset >> train_model
    [fetch_dataset, train_model] >> evaluate_model
