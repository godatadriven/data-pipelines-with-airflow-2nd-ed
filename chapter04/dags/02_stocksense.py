from urllib import request

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable


def _get_data(**kwargs):
    year, month, day, hour, *_ = kwargs["logical_date"].timetuple()
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    output_path = "/tmp/wikipageviews.gz"
    request.urlretrieve(url, output_path)

with DAG(
    dag_id="02_stocksense",
    start_date=pendulum.today("UTC").add(hours=-3),
    schedule=CronTriggerTimetable("@hourly", timezone="UTC"),
    max_active_runs=1,
    catchup=True
):
    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
    )
