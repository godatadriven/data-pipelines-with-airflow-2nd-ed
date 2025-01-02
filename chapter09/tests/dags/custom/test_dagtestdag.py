import os

from airflow.models import Connection
from airflow.providers.postgres.hooks.postgres import PostgresHook
from flaky import flaky
from pytest_docker_tools import fetch, container

from chapter09.dags.dagtestdag import dagtestdag
from chapter09.dags.custom.movielens_hook import MovielensHook

postgres_image = fetch(repository="postgres:16-alpine")
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

@flaky
def test_movielens_to_postgres_operator(mocker, postgres):
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
        return_value=[{"movieId": 1, "rating": 5, "userId": 123, "timestamp": 1725299750}, {"movieId": 2, "rating": 4, "userId": 456, "timestamp": 1525299750 }]
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
    pg_hook = PostgresHook()
    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count == 0

    dagtestdag.test()

    row_count = pg_hook.get_first("SELECT COUNT(*) FROM movielens")[0]
    assert row_count > 0
