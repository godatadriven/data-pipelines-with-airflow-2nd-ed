import datetime
import os
import sys
import uuid
from pathlib import Path

import pytest
from airflow.models import DAG

pytest_plugins = ["helpers_namespace"]

sys.path.insert(0, str(Path(os.path.dirname(__file__)).parent / "dags"))

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
