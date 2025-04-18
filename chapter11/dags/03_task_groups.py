import os

import pendulum
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.task_group import TaskGroup


def generate_tasks(dataset_name, raw_dir, processed_dir, preprocess_script, output_dir, dag):
    raw_path = os.path.join(raw_dir, dataset_name, "{ds_nodash}.json")
    processed_path = os.path.join(processed_dir, dataset_name, "{ds_nodash}.json")
    output_path = os.path.join(output_dir, dataset_name, "{ds_nodash}.json")

    fetch_task = BashOperator(
        task_id=f"fetch_{dataset_name}",
        bash_command=f"echo 'curl http://example.com/{dataset_name}.json > {raw_path}.json'",
        dag=dag,
    )

    preprocess_task = BashOperator(
        task_id=f"preprocess_{dataset_name}",
        bash_command=f"echo '{preprocess_script} {raw_path} {processed_path}'",
        dag=dag,
    )

    export_task = BashOperator(
        task_id=f"export_{dataset_name}",
        bash_command=f"echo 'cp {processed_path} {output_path}'",
        dag=dag,
    )

    fetch_task >> preprocess_task >> export_task

    # Return first and last task
    return fetch_task, export_task


with DAG(
    dag_id="03_task_groups",
    start_date=pendulum.today("UTC").add(days=-5),
    schedule="@daily",
) as dag:
    for dataset in ["sales", "customers"]:
        with TaskGroup(dataset, tooltip=f"Tasks for processing {dataset}"):
            generate_tasks(
                dataset_name=dataset,
                raw_dir="/data/raw",
                processed_dir="/data/processed",
                output_dir="/data/output",
                preprocess_script=f"preprocess_{dataset}.py",
                dag=dag,
            )
