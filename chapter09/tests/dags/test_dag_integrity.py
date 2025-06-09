"""Test integrity of DAGs."""

import glob
import os

import pytest
from airflow.models import DagBag

DAG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "dags/**/0*.py"
)
DAG_FILES = glob.glob(DAG_PATH, recursive=True)


@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_dag_integrity(dag_file, caplog):
    """Test integrity of DAGs."""
    DagBag(dag_folder=dag_file, include_examples=False)
    for record in caplog.records:
        if record.levelname == "ERROR":
            raise record.exc_info[1]
        elif "assumed to contain no DAGs" in record.message:
            assert False, f"No DAGs found in {dag_file}"
