import pendulum
import requests
from airflow import DAG
from airflow.decorators import task, task_group


@task
def fetch_ratings():
    "Retrieve the latest ratings from the movie reviews API. The number of reviews varies per request"
    data = requests.get("http://movie-reviews:8081/reviews/latest")
    return data.json()


@task_group(group_id="print_group")
def print_group(rating):
    @task
    def print_movie(rating):
        print(f"New rating for Movie: {rating["movie"]}")
        return rating

    @task
    def print_rating(rating):
        print(f"Rating: {rating["rating"]}")

    print_movie(rating) >> print_rating(rating)


with DAG(dag_id="08_dynamic_task_mapping_taskgroup",start_date=pendulum.today("UTC").add(days=-5), schedule="@daily") as dag:
    print_group.expand(rating=fetch_ratings())
