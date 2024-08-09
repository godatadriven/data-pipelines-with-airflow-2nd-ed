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

class AwaitMovielensRatingsSensor(BaseSensorOperator):
    """
    Deferable sensor that waits until an the movie ratings become available.
    """
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
        print(f"Movie Ratings are Available! for {{data_interval_start | ds}}-{{data_interval_end | ds}}") 
        return


class MovielensRatingsTrigger(BaseTrigger):
    def __init__(self,          
                 conn_id, 
                 start_date, 
                 end_date,
                 sleep_interval, 
            ):
        super().__init__()
        print('adentro init empiezo')
        self._sleep_interval = sleep_interval
        self._conn_id = conn_id
        self._start_date = start_date
        self._end_date = end_date
        print('adentro init termino')


    def serialize(self):
        return ("_triggers.MovielensRatingsTrigger", {
                "sleep_interval": self._sleep_interval,
                "conn_id": self._conn_id,
                "start_date": self._start_date,
                "end_date": self._end_date,
            }
        )

    async def run(self):
        print('adentro run')
        # Get an asynchronous version of our database backend. Note that this assumes that
        # the corresponding library (e.g. asyncpg) is installed in the triggerer env.
        
        hook = MovielensHook(self._conn_id)

        while True:
            try:
                next(hook.get_ratings(start_date=self._start_date, end_date=self._end_date, batch_size=1))
                # If no StopIteration is raised, the request returned at least one record.
                # This means that there are records for the given period, which we indicate
                # to Airflow by returning True.
                self.log.info(f"Found ratings for {self._start_date} to {self._end_date}, continuing!")
                return True
            except StopIteration:
                self.log.info(
                    f"Didn't find any ratings for {self._start_date} " f"to {self._end_date}, waiting..."
                )
                # If StopIteration is raised, we know that the request did not find
                # any records. This means that there a no ratings for the time period,
                # so we should return False.
                await asyncio.sleep(self.check_interval)
                return False
            finally:
                # Make sure we always close our hook's session.
                hook.close()




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

