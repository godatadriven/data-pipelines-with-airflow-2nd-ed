from dataclasses import dataclass

from .fetch import Dataset


@dataclass
class TrainResult:
    mlflow_run_id: str
    mlflow_artifact_path: str


def train_model(dataset: Dataset, epochs: int = 5, mlflow_artifact_path: str ="model") -> TrainResult:
    ...


