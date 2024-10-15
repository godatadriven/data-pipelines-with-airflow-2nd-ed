import pendulum
import requests
from airflow import DAG
from airflow.decorators import task


@task
def fetch_ratings():
    "Retrieve the latest ratings from the movie reviews API. The number of reviews varies per request"
    data = requests.get("http://movie-reviews:8081/reviews/latest")
    return data.json()


@task
def parse_rating(rating):
    print(f"New rating for Movie: {rating["movie"]}. Rating: {rating["rating"]}")


with DAG(dag_id="06_dynamic_task_mapping",start_date=pendulum.today("UTC").add(days=-5), schedule="@daily") as dag:
    parse_rating.expand(rating=fetch_ratings())
