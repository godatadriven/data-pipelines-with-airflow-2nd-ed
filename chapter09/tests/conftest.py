import datetime

import pytest
import uuid
from airflow.models import DAG

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
