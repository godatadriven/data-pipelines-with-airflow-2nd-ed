
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
            outlets=[Dataset(f"/data/supermarket_{dag_id}.csv") ],
        )



with DAG(
    dag_id="17_report",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=(
        (
            Dataset(f"/data/supermarket_1.csv") | Dataset(f"/data/supermarket_2.csv")
        ) 
        & Dataset(f"/data/supermarket_3.csv")),
):
     EmptyOperator(task_id="create_report")

