import dotenv
import typer

from .evaluate import evaluate_model
from .fetch import load_file, Dataset
from .train import train_model
import pandas as pd
import fsspec
import numpy as np
dotenv.load_dotenv()

app = typer.Typer()


@app.command()
def transfer(filename:str, source_path: str, dest_path: str):



    print(filename,source_path)    
    df = load_file(filename, source_path)

    print(df)


@app.command()
def upload():
    import os

    # To set/define environment variables
    os.environ['AWS_ENDPOINT_URL_S3'] = "http://localhost:9000"
    os.environ['AWS_ACCESS_KEY_ID'] =  "F4l5pE2uGsOPDEXAMPLE"
    os.environ['AWS_SECRET_ACCESS_KEY'] =  "K3OIYP1dPPvuIhybk1Tk3UfEEblUvtZetEXAMPLE"

    output_path =  "s3://data/2024-10-14/train"
    fs, base_path = fsspec.core.url_to_fs(output_path)

    fs.makedirs(base_path, exist_ok=True)
    
    with fs.open( base_path + "/images.npy", "wb") as file_:
        pd.save(file_, np.array([]))

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
