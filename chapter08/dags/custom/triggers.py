
import asyncio
from typing import Any
import uuid

from airflow.sensors.base import BaseSensorOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.utils.context import Context
from airflow.models import BaseOperator


from airflow.utils.decorators import apply_defaults

from custom.hooks import MovielensHook

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
        return ("custom.triggers.MovielensRatingsTrigger", {
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

        with MovielensHook(self._conn_id) as hook:
            found_records = False
            while not found_records:
                try:
                    # TODO: Also implement async get_ratings?
                    next(hook.get_ratings(start_date=self._start_date, end_date=self._end_date, batch_size=1))
                    # If no StopIteration is raised, the request returned at least one record.
                    # This means that there are records for the given period, which we indicate
                    # to Airflow by returning True.
                    self.log.info(f"Found ratings for {self._start_date} to {self._end_date}, continuing!")
                    found_records = True
                except StopIteration:
                    self.log.info(
                        f"Didn't find any ratings for {self._start_date} " f"to {self._end_date}, waiting..."
                    )
                    # If StopIteration is raised, we know that the request did not find
                    # any records. This means that there a no ratings for the time period,
                    # so we should return False.
                    await asyncio.sleep(self.check_interval)

        yield TriggerEvent(str(uuid.uuid4()))
