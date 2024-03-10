import dotenv
import typer

from .evaluate import evaluate_model
from .fetch import fetch_datasets, Dataset
from .train import train_model

dotenv.load_dotenv()

app = typer.Typer()


@app.command()
def fetch(train_output_path: str, test_output_path: str):
    train_dataset, test_dataset = fetch_datasets()
    train_dataset.save(train_output_path)
    test_dataset.save(test_output_path)


@app.command()
def train(train_dataset_path: str, epochs: int = 5):
    dataset = Dataset.load(train_dataset_path)
    result = train_model(dataset, epochs=epochs)
    print(result.mlflow_run_id)


@app.command()
def evaluate(test_dataset_path: str, mlflow_run_id: str):
    dataset = Dataset.load(test_dataset_path)
    evaluate_model(test_dataset=dataset, mlflow_run_id=mlflow_run_id)


if __name__ == "__main__":
    app()
