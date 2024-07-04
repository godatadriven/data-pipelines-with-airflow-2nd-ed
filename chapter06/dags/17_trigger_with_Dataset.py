
"""
    Listing: 6.8, 6.9
    Figure: 6.23, 6.24
"""


import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.datasets import Dataset

for dag_id in range(1, 4):

    with DAG(
        dag_id=f"17_etl_{dag_id}",
        start_date=pendulum.today("UTC").add(days=-3),
        schedule=None,
    ):
        etl =  EmptyOperator(
            task_id="save_data",
            outlets=[Dataset(f"/supermarket_{dag_id}.csv") ],
        )



with DAG(
    dag_id="17_report",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=(
        (
            Dataset(f"/supermarket_1.csv") | Dataset(f"/supermarket_2.csv")
        ) 
        & Dataset(f"/supermarket_3.csv")),
):
     EmptyOperator(task_id="create_report")

