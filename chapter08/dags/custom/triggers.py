import asyncio
from typing import Any

from airflow.sensors.base import BaseSensorOperator
from airflow.triggers.base import BaseTrigger, TriggerEvent
from airflow.utils.context import Context

from airflow.utils.decorators import apply_defaults

from custom.hooks import MovielensHook
import uuid

class MovielensSensorAsync(BaseSensorOperator):
    """
    Deferable sensor that waits until an XCom becomes available.
    """

    template_fields = ("_start_date", "_end_date")


    @apply_defaults
    def __init__(self,  
                 conn_id, start_date=f"{{data_interval_start | ds}}", 
                 end_date=f"{{data_interval_end | ds}}",
                 sleep_interval: int = 30, 
                 **kwargs
            ):
        super().__init__(**kwargs)
        self._sleep_interval = sleep_interval
        self._conn_id = conn_id
        self._start_date = start_date
        self._end_date = end_date
        self._timeout = kwargs.get('timeout')

    def execute(self, context: Context) -> None:

        self.defer(
            trigger=MovielensTrigger(
                conn_id=self._conn_id,
                sleep_interval=self._sleep_interval,
                start_date=self._start_date,
                end_date=self._end_date,
            ),
            method_name='execute_complete',
            timeout = self._timeout
        )

    def execute_complete(self,context: Context, event: dict[str, Any] | None = None ) -> bool:

        print(f"Movie Ratings are Available! for {self._start_date}-{self._end_date}") 
        return True


class MovielensTrigger(BaseTrigger):
    def __init__(self,          
                 conn_id, 
                 start_date, 
                 end_date,
                 sleep_interval, 

            ):
        super().__init__()
        self._sleep_interval = sleep_interval
        self._conn_id = conn_id
        self._start_date = start_date
        self._end_date = end_date


    def serialize(self):
        return ("custom.triggers.MovielensTrigger", {
                "sleep_interval": self._sleep_interval,
                "conn_id": self._conn_id,
                "start_date": self._start_date,
                "end_date": self._end_date,
            }
        )
  
    async def run(self):
        # Get an asynchronous version of our database backend. Note that this assumes that
        # the corresponding library (e.g. asyncpg) is installed in the triggerer env.

        with MovielensHook(self._conn_id) as hook:
            found_records = True
            while not found_records:
                try:
                    next(hook.get_ratings(start_date=self._start_date, end_date=self._end_date, batch_size=1))
                    # If no StopIteration is raised, the request returned at least one record.
                    # This means that there are records for the given period, which we indicate
                    # to Airflow by returning True.
                    self.log.info(f"Found ratings for {self._start_date} to {self._end_date}, continuing!")
                    found_records = True
                except StopIteration:
                    self.log.info(
                        f"Didn't find any ratings for {self._start_date} to {self._end_date}, waiting..."
                    )
                    # If StopIteration is raised, we know that the request did not find
                    # any records. This means that there a no ratings for the time period,
                    # so we should wait for a bit and retry.
                    await asyncio.sleep(self.check_interval)
        
        yield TriggerEvent(str(uuid.uuid4()))