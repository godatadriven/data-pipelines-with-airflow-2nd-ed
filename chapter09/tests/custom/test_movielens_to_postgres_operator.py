import datetime
import os

import pytest
from airflow import DAG
from airflow.models import Connection
from airflow.providers.postgres.hooks.postgres import PostgresHook
from pytest_docker_tools import fetch, container

from chapter09.custom.movielens_hook import MovielensHook
from chapter09.custom.movielens_to_postgres_operator import MovielensToPostgresOperator

postgres_image = fetch(repository="postgres:11.1-alpine")
postgres = container(
    image="{postgres_image.id}",
    environment={
        "POSTGRES_USER": "testuser",
        "POSTGRES_PASSWORD": "testpass",
    },
    ports={"5432/tcp": None},
    volumes={
        os.path.join(os.path.dirname(__file__), "postgres-init.sql"): {
            "bind": "/docker-entrypoint-initdb.d/postgres-init.sql"
        }
    },
)


def test_movielens_to_postgres_operator(mocker, postgres, test_dag):
    mocker.patch.object(
        MovielensHook,
        "get_connection",
        return_value=Connection(
            conn_id="test",
            login="airflow",
            password="airflow",
        ),
    )
    mocker.patch.object(
        MovielensHook,
        "get_ratings",
        return_value=[{"movieId": 1, "rating": 5}, {"movieId": 2, "rating": 4}]
    )
    mocker.patch.object(
        PostgresHook,
        "get_connection",
        return_value=Connection(
            conn_id="postgres",
            conn_type="postgres",
            host="localhost",
            login="testuser",
            password="testpass",
            port=postgres.ports["5432/tcp"][0]
        ),
    )
    # test_dag2 = DAG(
    #     "test_dag3",
    #     default_args={
    #         "owner": "airflow",
    #         "start_date": datetime.datetime(2024, 1, 1),
    #     },
    #     schedule="@daily",
    # )
    #
    task = MovielensToPostgresOperator(
        task_id="test",
        movielens_conn_id="test",
        start_date="{{ data_interval_start | ds }}",
        end_date="{{ data_interval_end | ds}}",
        postgres_conn_id="postgres",
        insert_query=(
            "INSERT INTO movielens (movieId,rating,scrapeTime) "
            "VALUES ({0}, '{{ macros.datetime.now() }}')"
        ),
        dag=test_dag,
    )
    pg_hook = PostgresHook()
    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count == 0

    task.run(
        start_date=test_dag.default_args["start_date"],
        end_date=test_dag.default_args["start_date"],
    )

    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count > 0
