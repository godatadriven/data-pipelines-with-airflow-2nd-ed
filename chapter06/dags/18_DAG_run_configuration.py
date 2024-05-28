import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator

with DAG(
    dag_id="18_without_dag_run_configuration",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
    default_args={"depends_on_past": True},
):
    for supermarket_id in range(1, 5):
        copy = EmptyOperator(task_id=f"copy_to_raw_supermarket_{supermarket_id}")
        process = EmptyOperator(task_id=f"process_supermarket_{supermarket_id}")
        create_metrics = EmptyOperator(task_id=f"create_metrics_{supermarket_id}")
        copy >> process >> create_metrics


with DAG(
    dag_id="18_with_dag_run_configuration",
    start_date=pendulum.today("UTC").add(days=-3),
    schedule="0 16 * * *",
    description="A batch workflow for ingesting supermarket promotions data, demonstrating the PythonSensor.",
    default_args={"depends_on_past": True},
):
    copy = EmptyOperator(task_id="copy_to_raw")
    process = EmptyOperator(task_id="process")
    create_metrics = EmptyOperator(task_id="create_metrics")
    copy >> process >> create_metrics
