# """
# Documentation of pageview format: https://wikitech.wikimedia.org/wiki/Analytics/Data_Lake/Traffic/Pageviews
# """

from urllib import request

import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.timetables.trigger import CronTriggerTimetable


def _get_data(year, month, day, hour, output_path, **_):
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    request.urlretrieve(url, output_path)


def _fetch_pageviews(pagenames, logical_date):
    result = dict.fromkeys(pagenames, 0)
    with open(f"/tmp/wikipageviews-{ logical_date.format('YYYYMMDDHH') }") as f:
        for line in f:
            domain_code, page_title, view_counts, _ = line.split(" ")
            if domain_code == "en" and page_title in pagenames:
                result[page_title] = view_counts

    with open("/tmp/postgres_query.sql", "w") as f:
        for pagename, pageviewcount in result.items():
            f.write(
                "INSERT INTO pageview_counts VALUES ("
                f"'{pagename}', {pageviewcount}, '{logical_date}'"
                ")"
                "ON CONFLICT (pagename, datetime) DO NOTHING;\n"
            )


with DAG(
    dag_id="09_postgres_call",
    start_date=pendulum.today("UTC").add(hours=-3),
    schedule=CronTriggerTimetable("@hourly", timezone="UTC"),
    template_searchpath="/tmp",
    max_active_runs=1,
    catchup=True
):
    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
        op_kwargs={
            "year": "{{ logical_date.year }}",
            "month": "{{ logical_date.month }}",
            "day": "{{ logical_date.day }}",
            "hour": "{{ logical_date.hour }}",
            "output_path": "/tmp/wikipageviews-{{ logical_date.format('YYYYMMDDHH') }}.gz",
        },
    )

    extract_gz = BashOperator(task_id="extract_gz", bash_command="gunzip --force /tmp/wikipageviews-{{ logical_date.format('YYYYMMDDHH') }}.gz")

    fetch_pageviews = PythonOperator(
        task_id="fetch_pageviews",
        python_callable=_fetch_pageviews,
        op_kwargs={"pagenames": {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}},
    )

    write_to_postgres = SQLExecuteQueryOperator(
        task_id="write_to_postgres",
        conn_id="my_postgres",
        sql="postgres_query.sql",
        return_last=False,
    )

    get_data >> extract_gz >> fetch_pageviews >> write_to_postgres
