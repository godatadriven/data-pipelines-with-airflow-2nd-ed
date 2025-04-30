from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable

from custom.operators import MovielensFetchRatingsOperator
from custom.triggers import MovielensSensorAsync

with DAG(
    dag_id="05_deferrable_sensor",
    description="Fetches ratings from the Movielens API, with a deferrable custom sensor.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 10),
    schedule=CronDataIntervalTimetable("@daily", "UTC"),
    catchup=True
):
    wait_for_ratings = MovielensSensorAsync(
        task_id="wait_for_ratings",
        conn_id="movielens",
        start_date="{{data_interval_start | ds}}",
        end_date="{{data_interval_end | ds}}",
        execution_timeout= timedelta(seconds=60),
    )

    fetch_ratings = MovielensFetchRatingsOperator(
        task_id="fetch_ratings",
        conn_id="movielens",
        start_date="{{data_interval_start | ds}}",
        end_date="{{data_interval_end | ds}}",
        output_path="/data/custom_sensor/{{data_interval_start | ds}}.json",
    )

    wait_for_ratings >> fetch_ratings
