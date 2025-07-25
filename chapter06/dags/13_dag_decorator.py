"""
Listing: 5.29
Figure: 5.19
"""

import uuid

import pendulum
from airflow.sdk import dag, task


@dag(
    dag_id="13_dag_decorator",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="@daily",
    catchup=True,
)
def taskflow_api_decorator():

    @task
    def train_model():
        model_id = str(uuid.uuid4())
        return model_id

    @task
    def deploy_model(model_id: str):
        print(f"Deploying model {model_id}")

    model_id = train_model()
    deploy_model(model_id)
    deploy_model(model_id)

taskflow_api_decorator()

