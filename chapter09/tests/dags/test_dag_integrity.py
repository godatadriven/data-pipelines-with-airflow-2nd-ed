"""Test integrity of DAGs."""

import glob
import os

import pytest
from airflow.dag_processing.processor import DagFileProcessor

DAG_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "dags/*.py"
)
DAG_FILES = glob.glob(DAG_PATH)


@pytest.mark.parametrize("dag_file", DAG_FILES)
def test_dag_integrity(dag_file, caplog):
    """Test integrity of DAGs."""
    DagFileProcessor._get_dagbag(dag_file)
    # The DagBag's _process_modules function catches and logs all exceptions, so we parse the logs to raise them here
    for record in caplog.records:
        if record.levelname == "ERROR":
            raise record.exc_info[1]
        elif "assumed to contain no DAGs" in record.message:
            assert False, f"No DAGs found in {dag_file}"
