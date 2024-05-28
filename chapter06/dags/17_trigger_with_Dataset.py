
import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.datasets import Dataset

for dag_id in range(1, 4):

    with DAG(
        dag_id=f"17_etl_{dag_id}",
        start_date=pendulum.today("UTC").add(days=-3),
        schedule="0 16 * * *",
    ):
        etl =  EmptyOperator(
            task_id="save_data",
            outlets=[Dataset(f"/data/supermarket_{dag_id}") ],
        )

dag1, dag2, dag3 = [ 
    Dataset(f"/data/supermarket_{dag_id}") for dag_id in range(1, 4) 
    ]


with DAG(
    dag_id="17_report",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule=((dag1 | dag2) & dag3),
):
    report = EmptyOperator(task_id="compute_differences")

