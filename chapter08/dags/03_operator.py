from datetime import datetime

from airflow.sdk import DAG
from airflow.timetables.interval import CronDataIntervalTimetable
from custom.operators import MovielensFetchRatingsOperator

with DAG(
    dag_id="03_operator",
    description="Fetches ratings from the Movielens API using a custom operator.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 10),
    schedule=CronDataIntervalTimetable("@daily", "UTC"),
    catchup=True
):
    MovielensFetchRatingsOperator(
        task_id="fetch_ratings",
        conn_id="movielens",
        start_date="{{data_interval_start | ds}}",
        end_date="{{data_interval_end | ds}}",
        output_path="/data/custom_operator/{{data_interval_start | ds}}.json",
    )
