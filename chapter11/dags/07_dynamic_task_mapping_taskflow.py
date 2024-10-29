import pendulum
import requests
from airflow import DAG
from airflow.decorators import task


@task
def fetch_ratings():
    data = requests.get("http://movie-reviews:8081/reviews/latest")
    return data.json() #A


@task
def print_rating(rating): #B
    print(f"New rating for Movie: {rating["movie"]}. Rating: {rating["rating"]}")


with DAG(dag_id="07_dynamic_task_mapping_taskflow",start_date=pendulum.today("UTC").add(days=-5), schedule="@daily") as dag:
    print_rating.expand(rating=fetch_ratings()) #C
