import datetime

from airflow import DAG

from .custom.movielens_to_postgres_operator import MovielensToPostgresOperator

dagtestdag = DAG(
    "dagtestdag",
    default_args={
        "owner": "airflow",
        "start_date": datetime.datetime(2024, 1, 1),
    },
    schedule=None,
)

task = MovielensToPostgresOperator(
    task_id="retrieve_and_insert",
    movielens_conn_id="test",
    start_date="{{ data_interval_start | ds }}",
    end_date="{{ data_interval_end | ds}}",
    postgres_conn_id="postgres",
    insert_query=(
        "INSERT INTO movielens (movieId,rating,ratingTimestamp,userId,scrapeTime) "
        "VALUES ({0}, '{{ macros.datetime.now() }}')"
    ),
    dag=dagtestdag
)
