"""
Listing: 5.3, 5.4, 5.5, 5.6
Figure: 5.3
"""
import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="01_rocket_pipeline_dependencies",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="@daily",
):
    start = EmptyOperator(task_id="start")

    fetch_sales = EmptyOperator(task_id="fetch_sales")
    clean_sales = EmptyOperator(task_id="clean_sales")

    fetch_weather = EmptyOperator(task_id="fetch_weather")
    clean_weather = EmptyOperator(task_id="clean_weather")

    join_datasets = EmptyOperator(task_id="join_datasets")
    train_model = EmptyOperator(task_id="train_model")
    deploy_model = EmptyOperator(task_id="deploy_model")

    start >> [fetch_sales, fetch_weather]
    fetch_sales >> clean_sales
    fetch_weather >> clean_weather
    [clean_sales, clean_weather] >> join_datasets
    join_datasets >> train_model >> deploy_model
