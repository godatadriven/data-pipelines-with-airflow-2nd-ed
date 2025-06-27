import pendulum
import requests
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.timetables.trigger import CronTriggerTimetable


def _fetch_ratings(ti):
    "Retrieve the latest ratings from the movie reviews API. The number of reviews varies per request"
    data = requests.get("http://movie-reviews-api:8081/reviews/latest")
    ti.xcom_push(key="movie_ratings", value=[[x] for x in data.json()])


def _print_rating(ti):
    data = ti.xcom_pull(key="movie_ratings", task_ids="fetch_ratings")
    for rating in data:
        print(f"New rating for Movie: {rating[0]["movie"]}. Rating: {rating[0]["rating"]}")

def add_function(x: int, y: int):
    return x + y

with DAG(dag_id="09_no_dynamic_task_mapping",
         start_date=pendulum.today("UTC").add(days=-5),
         schedule=CronTriggerTimetable("0 16 * * *", timezone="UTC")):
    fetch_ratings = PythonOperator(
        task_id="fetch_ratings",
        python_callable=_fetch_ratings
    )

    print_rating = PythonOperator(
        task_id="print_rating",
        python_callable=_print_rating
    )


    added_values = PythonOperator.partial(
        task_id="add",
        python_callable=add_function,
        op_kwargs={"y": 10}
    ).expand(op_args=[[1], [2], [3]])

    fetch_ratings >> print_rating >> added_values



def add_function(x: int, y: int):
    return x + y

added_values = PythonOperator.partial( #A
    task_id="add",
    python_callable=add_function,
    op_kwargs={"y": 10} #B
).expand(op_args=[[1], [2], [3]])  #C