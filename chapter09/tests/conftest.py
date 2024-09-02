import datetime

import pytest
import uuid
from airflow.models import DAG, BaseOperator

pytest_plugins = ["helpers_namespace"]


@pytest.fixture
def test_dag():
    return DAG(
        f"test_dag_{uuid.uuid4()}",
        default_args={
            "owner": "airflow",
            "start_date": datetime.datetime(2024, 1, 1),
        },
        schedule="@daily",
    )


@pytest.helpers.register
def run_airflow_task(task: BaseOperator, dag: DAG):
    dag.clear()
    task.run(
        start_date=dag.default_args["start_date"],
        end_date=dag.default_args["start_date"],
        ignore_ti_state=True,
    )
