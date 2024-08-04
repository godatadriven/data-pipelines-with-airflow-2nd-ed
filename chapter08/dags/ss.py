from airflow import DAG
from datetime import timedelta, datetime
from airflow.triggers.temporal import TimeDeltaTrigger
from airflow.models.baseoperator import BaseOperator
from airflow.triggers.base import BaseTrigger

import logging

# get Airflow logger
log = logging.getLogger('airflow.task')


class MovielensRatingsTrigger(BaseTrigger):
    def __init__(self,          
             
            ):
        super().__init__()

    def serialize(self):
        ...

    async def run(self):
        print('adentro run')
        # Get an asynchronous version of our database backend. Note that this assumes that
        # the corresponding library (e.g. asyncpg) is installed in the triggerer env.
        
        ...



class TestDefer(BaseOperator):
    def execute(self, context):
        log.info("--- execute --")

        self.defer(
            trigger=MovielensRatingsTrigger(
                
            ),
            method_name="func",
        )

    def func(self, context, event=None):
        log.info("--- func ----")
        pass

with DAG(
    "def_dag",
    schedule_interval='@daily',
    start_date=datetime(2024, 7, 20),
) as dag:

    t = TestDefer(task_id="defer_task")