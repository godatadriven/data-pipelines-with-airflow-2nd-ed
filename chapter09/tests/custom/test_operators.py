from airflow.models import Connection

from custom.hooks import MovielensHook
from custom.operators import MovielensPopularityOperator


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
    task = MovielensPopularityOperator(
        task_id="test_id",
        conn_id="test",
        start_date="2015-01-01",
        end_date="2015-01-03",
        top_n=5,
    )
    result = task.execute(context=None)
    assert len(result) == 5
