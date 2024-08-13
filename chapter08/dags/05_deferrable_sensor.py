import datetime as dt

from airflow import DAG
from custom.operators import MovielensFetchRatingsOperator
# from custom.deferrable_sensors import AwaitMovielensRatingsSensor



import asyncio
from typing import Any

from airflow.sensors.base import BaseSensorOperator
from airflow.triggers.base import BaseTrigger
from airflow.utils.context import Context
from airflow.models import BaseOperator


from airflow.utils.decorators import apply_defaults

from custom.hooks import MovielensHook
from custom.triggers import MovielensRatingsTrigger

class AwaitMovielensRatingsSensor(BaseSensorOperator):
    """
    Deferable sensor that waits until an the movie ratings become available.
    """

    template_fields = ("_start_date", "_end_date")

    @apply_defaults
    def __init__(self,
                 conn_id, start_date="{{data_interval_start | ds}}",
                 end_date="{{data_interval_end | ds}}",
                 sleep_interval: int = 30,
                 **kwargs
            ):
        super().__init__(**kwargs)
        self._sleep_interval = sleep_interval
        self._conn_id = conn_id
        self._start_date = start_date
        self._end_date = end_date


    def execute(self, context: Context) -> None:
        print('adentro execute')
        self.defer(
            trigger=MovielensRatingsTrigger(
                conn_id=self._conn_id,
                sleep_interval=self._sleep_interval,
                start_date=self._start_date,
                end_date=self._end_date,
            ),
            method_name='execute_completed'
        )
        print('adentro execute termino')


    def execute_completed(
        self,
        context: Context,
        event: dict[str, Any] | None = None,
    ) -> None:
        print(context)
        # TODO: Fix templating (from context or operator?)
        print(f"Movie Ratings are Available! for {{data_interval_start | ds}}-{{data_interval_end | ds}}")
        return True # TODO: How do we handle failure (e.g. timeout?) In the trigger?


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
