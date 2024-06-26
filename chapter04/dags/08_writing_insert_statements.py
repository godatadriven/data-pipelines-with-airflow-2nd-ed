from urllib import request

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator


def _get_data(year, month, day, hour, output_path, **_):
    url = (
        "https://dumps.wikimedia.org/other/pageviews/"
        f"{year}/{year}-{month:0>2}/pageviews-{year}{month:0>2}{day:0>2}-{hour:0>2}0000.gz"
    )
    request.urlretrieve(url, output_path)


def _fetch_pageviews(pagenames, data_interval_start, **_):
    result = dict.fromkeys(pagenames, 0)
    with open(f"/tmp/wikipageviews-{ data_interval_start.format('YYYYMMDDHH') }") as f:
        for line in f:
            domain_code, page_title, view_counts, _ = line.split(" ")
            if domain_code == "en" and page_title in pagenames:
                result[page_title] = view_counts

    with open("/tmp/postgres_query.sql", "w") as f:
        for pagename, pageviewcount in result.items():
            f.write(
                "INSERT INTO pageview_counts VALUES ("
                f"'{pagename}', {pageviewcount}, '{data_interval_start}'"
                ");\n"
            )


with DAG(
    dag_id="08_writing_insert_statements",
    start_date=pendulum.today("UTC").add(days=-1),
    schedule="@hourly",
    max_active_runs=1,
):
    get_data = PythonOperator(
        task_id="get_data",
        python_callable=_get_data,
        op_kwargs={
            "year": "{{ data_interval_start.year }}",
            "month": "{{ data_interval_start.month }}",
            "day": "{{ data_interval_start.day }}",
            "hour": "{{ data_interval_start.hour }}",
            "output_path": "/tmp/wikipageviews-{{ data_interval_start.format('YYYYMMDDHH') }}.gz",
        },
    )

    extract_gz = BashOperator(task_id="extract_gz", bash_command="gunzip --force /tmp/wikipageviews-{{ data_interval_start.format('YYYYMMDDHH') }}.gz")

    fetch_pageviews = PythonOperator(
        task_id="fetch_pageviews",
        python_callable=_fetch_pageviews,
        op_kwargs={"pagenames": {"Google", "Amazon", "Apple", "Microsoft", "Facebook"}},
    )

    get_data >> extract_gz >> fetch_pageviews
