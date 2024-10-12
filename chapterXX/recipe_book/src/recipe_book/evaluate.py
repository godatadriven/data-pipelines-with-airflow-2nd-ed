from .fetch import Dataset


def evaluate_model(test_dataset: Dataset, mlflow_run_id: str):
    # Delay imports to speed up CLI.
    import mlflow.keras

    test_images = test_dataset.images / 255.0
    test_images = test_images.reshape(test_images.shape[0], 28, 28, 1)

    model = mlflow.keras.load_model(f"runs:/{mlflow_run_id}/model")

    with mlflow.start_run(run_id=mlflow_run_id):
        _, test_acc = model.evaluate(test_images, test_dataset.labels)
        mlflow.log_metrics({"accuracy": test_acc})
