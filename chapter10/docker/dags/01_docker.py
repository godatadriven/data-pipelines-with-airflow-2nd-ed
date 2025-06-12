import os
from datetime import datetime

from airflow.providers.docker.operators.docker import DockerOperator
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
from docker.types import Mount

with DAG(
    dag_id="01_docker",
    description="Fetches ratings from the Movielens API using Docker.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule=CronDataIntervalTimetable("@daily", "UTC"),
    catchup=True,
):
    fetch_ratings = DockerOperator(
        task_id="fetch_ratings",
        image="manning-airflow/movielens-fetch",
        command=[
            "fetch-ratings",
            "--start_date",
            "{{ data_interval_start | ds }}",
            "--end_date",
            "{{ data_interval_end | ds }}",
            "--output_path",
            "/data/ratings/{{ data_interval_start | ds }}.json",
            "--user",
            os.environ["MOVIELENS_USER"],
            "--password",
            os.environ["MOVIELENS_PASSWORD"],
            "--host",
            os.environ["MOVIELENS_HOST"],
        ],
        network_mode="docker_default",
        # Note: this host path is on the HOST, not in the Airflow docker container.
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        mount_tmp_dir=False,
    )

    rank_movies = DockerOperator(
        task_id="rank_movies",
        image="manning-airflow/movielens-rank",
        command=[
            "rank-movies",
            "--input_path",
            "/data/ratings/{{ data_interval_start | ds }}.json",
            "--output_path",
            "/data/rankings/{{ data_interval_start | ds }}.csv",
        ],
        network_mode="docker_default",
        mounts=[Mount(source="docker_airflow-data-volume", target="/data", type="volume")],
        mount_tmp_dir=False,
    )

    fetch_ratings >> rank_movies
