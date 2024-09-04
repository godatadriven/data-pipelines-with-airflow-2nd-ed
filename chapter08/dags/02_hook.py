from datetime import datetime
import json
import logging
import os

from airflow import DAG
from airflow.operators.python import PythonOperator
from custom.hooks import MovielensHook

with DAG(
    dag_id="02_hook",
    description="Fetches ratings from the Movielens API using a custom hook.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 10),
    schedule="@daily",
):

    def _fetch_ratings(conn_id, templates_dict, batch_size=1000, **_):
        logger = logging.getLogger(__name__)

        start_date = templates_dict["start_date"]
        end_date = templates_dict["end_date"]
        output_path = templates_dict["output_path"]

        logger.info(f"Fetching ratings for {start_date} to {end_date}")
        hook = MovielensHook(conn_id=conn_id)
        ratings = list(hook.get_ratings(start_date=start_date, end_date=end_date, batch_size=batch_size))
        logger.info(f"Fetched {len(ratings)} ratings")

        logger.info(f"Writing ratings to {output_path}")

        # Make sure output directory exists.
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

        with open(output_path, "w") as file_:
            json.dump(ratings, fp=file_)

    PythonOperator(
        task_id="fetch_ratings",
        python_callable=_fetch_ratings,
        op_kwargs={"conn_id": "movielens"},
        templates_dict={
            "start_date": "{{data_interval_start | ds}}",
            "end_date": "{{data_interval_end | ds}}",
            "output_path": "/data/custom_hook/{{data_interval_start | ds}}.json",
        },
    )
