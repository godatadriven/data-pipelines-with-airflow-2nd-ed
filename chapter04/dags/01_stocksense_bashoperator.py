import pendulum
from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.timetables.trigger import CronTriggerTimetable

with DAG(
    dag_id="01_stocksense_bashoperator",
    start_date=pendulum.today("UTC").add(hours=-3),
    schedule=CronTriggerTimetable("@hourly", timezone="UTC"),
    max_active_runs=1,
    catchup=True
):
    get_data = BashOperator(
        task_id="get_data",
        bash_command=(
            "curl -o /tmp/wikipageviews.gz "
            "https://dumps.wikimedia.org/other/pageviews/"
            "{{ logical_date.year }}/"
            "{{ logical_date.year }}-{{ '{:02}'.format(logical_date.month) }}/"
            "pageviews-{{ logical_date.year }}"
            "{{ '{:02}'.format(logical_date.month) }}"
            "{{ '{:02}'.format(logical_date.day) }}-"
            "{{ '{:02}'.format(logical_date.hour) }}0000.gz"
        ),
    )
