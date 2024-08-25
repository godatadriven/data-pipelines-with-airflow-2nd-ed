from airflow.models import Connection

from custom.movielens_hook import MovielensHook
from custom.movielens_popularity_operator import MovielensPopularityOperator


def test_movielenspopularityoperator(mocker):
    mocker.patch.object(
        MovielensHook,
        "get_connection",
        return_value=Connection(
            host="airflow",
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
    task = MovielensPopularityOperator(
        task_id="test_id",
        conn_id="test",
        start_date="2015-01-01",
        end_date="2015-01-03",
        top_n=5,
        min_ratings=1
    )
    result = task.execute(context=None)
    assert len(result) == 2
