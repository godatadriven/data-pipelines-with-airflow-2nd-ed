import pendulum
import requests
from airflow import DAG
from airflow.operators.python import PythonOperator


def _fetch_ratings():
    "Retrieve the latest ratings from the movie reviews API. The number of reviews varies per request"
    data = requests.get("http://movie-reviews-api:8081/reviews/latest")
    return [[x] for x in data.json()]


def _print_rating(rating):
    print(f"New rating for Movie: {rating["movie"]}. Rating: {rating["rating"]}")


with DAG(dag_id="06_dynamic_task_mapping",start_date=pendulum.today("UTC").add(days=-5), schedule="@daily"):
    fetch_ratings = PythonOperator(
        task_id="fetch_ratings",
        python_callable=_fetch_ratings
    )

    print_rating = PythonOperator.partial(
        task_id="print_rating",
        python_callable=_print_rating
    ).expand(op_args=fetch_ratings.output)

    fetch_ratings >> print_rating
