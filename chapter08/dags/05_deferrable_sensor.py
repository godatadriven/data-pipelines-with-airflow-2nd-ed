import datetime as dt

from airflow import DAG
from custom.operators import MovielensFetchRatingsOperator

from custom.deferrable_sensors import AwaitMovielensRatingsSensor

with DAG(
    dag_id="05_deferrable_sensor",
    description="Fetches ratings from the Movielens API, with a deferrable custom sensor.",
    start_date=dt.datetime(2023, 1, 1),
    end_date=dt.datetime(2023, 1, 10),
    schedule="@daily",
):
    wait_for_ratings = AwaitMovielensRatingsSensor(
        task_id="wait_for_ratings",
        conn_id="movielens",
        start_date="{{data_interval_start | ds}}",
        end_date="{{data_interval_end | ds}}",
    )

    fetch_ratings = MovielensFetchRatingsOperator(
        task_id="fetch_ratings",
        conn_id="movielens",
        start_date="{{data_interval_start | ds}}",
        end_date="{{data_interval_end | ds}}",
        output_path="/data/custom_sensor/{{data_interval_start | ds}}.json",
    )

    wait_for_ratings >> fetch_ratings
