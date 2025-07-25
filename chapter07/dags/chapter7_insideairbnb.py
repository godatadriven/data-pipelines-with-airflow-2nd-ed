from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
from custom.postgres_to_s3_operator import PostgresToS3Operator

with DAG(
    dag_id="chapter7_insideairbnb",
    start_date=datetime(2025, 3, 1),
    end_date=datetime(2025, 4, 1),
    schedule=CronDataIntervalTimetable("@monthly", "UTC"),
    catchup=True,
):

    download_from_postgres = PostgresToS3Operator(
        task_id="download_from_postgres",
        postgres_conn_id="inside_airbnb",
        query="SELECT * FROM listings WHERE download_date BETWEEN '{{ data_interval_start | ds }}' AND '{{ data_interval_end | ds }}'",
        s3_conn_id="locals3",
        s3_bucket="inside-airbnb",
        s3_key="listing-{{ ds }}.csv",
    )

    crunch_numbers = DockerOperator(
        task_id="crunch_numbers",
        image="manning-airflow/numbercruncher",
        api_version="auto",
        auto_remove="success",
        docker_url="unix://var/run/docker.sock",
        network_mode="host",
        environment={
            "S3_ENDPOINT": "localhost:9000",
            "S3_ACCESS_KEY": "secretaccess",
            "S3_SECRET_KEY": "secretkey",
        },
    )

    download_from_postgres >> crunch_numbers
