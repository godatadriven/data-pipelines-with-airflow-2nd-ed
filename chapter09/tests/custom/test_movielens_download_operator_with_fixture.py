import datetime

import pytest
from airflow.models import DAG, Connection

from chapter09.custom.movielens_download_operator import MovielensDownloadOperator
from chapter09.custom.movielens_hook import MovielensHook


def test_movielens_operator(tmp_path, mocker, test_dag):
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

    task = MovielensDownloadOperator(
        task_id="test",
        conn_id="testconn",
        start_date="{{ data_interval_start }}",
        end_date="{{ data_interval_end }}",
        output_path=str(tmp_path / "{{ ds }}.json"),
        dag=test_dag,
    )

    task.run(
        start_date=test_dag.default_args["start_date"],
        end_date=test_dag.default_args["start_date"],
    )
