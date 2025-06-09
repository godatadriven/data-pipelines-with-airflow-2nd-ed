import datetime

from airflow import DAG
from airflow.models import Connection
from custom.movielens_download_operator import MovielensDownloadOperator
from custom.movielens_hook import MovielensHook


def test_movielens_operator(tmp_path, mocker):
    mocker.patch.object(
        MovielensHook,
        "get_connection",
        return_value=Connection(
            conn_id="test", login="airflow", password="airflow"
        ),
    )
    mocker.patch.object(
        MovielensHook,
        "get_ratings",
        return_value=[{"movieId": 1, "rating": 5}, {"movieId": 2, "rating": 4}]
    )

    dag = DAG(
        "test_dag",
        default_args={
            "owner": "airflow",
            "start_date": datetime.datetime(2024, 1, 1),
        },
        schedule="@daily",
    )

    task = MovielensDownloadOperator(
        task_id="test",
        conn_id="testconn",
        start_date="{{ data_interval_start | ds }}",
        end_date="{{ data_interval_end | ds }}",
        output_path=str(tmp_path / "{{ ds }}.json"),
        dag=dag,
    )

    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
    )
