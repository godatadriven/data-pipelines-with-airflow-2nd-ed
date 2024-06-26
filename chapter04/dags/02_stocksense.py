from urllib import request

import pendulum
from airflow import DAG
from airflow.operators.python import PythonOperator


def _get_data(**kwargs):
    year, month, day, hour, *_ = kwargs["data_interval_start"].timetuple()
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    output_path = "/tmp/wikipageviews.gz"
    request.urlretrieve(url, output_path)


with DAG(
    dag_id="02_stocksense",
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@hourly",
    max_active_runs=1,
):
    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
    )
