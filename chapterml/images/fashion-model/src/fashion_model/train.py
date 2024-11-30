from dataclasses import dataclass

from .fetch import Dataset


@dataclass
class TrainResult:
    mlflow_run_id: str
    mlflow_artifact_path: str


def train_model(dataset: Dataset, epochs: int = 5, mlflow_artifact_path: str ="model") -> TrainResult:
    # Delay imports to speed up CLI.
    import keras
    import mlflow.keras
    import tensorflow as tf

    with mlflow.start_run() as run:
        # Log model hyperparameters.
        mlflow.log_params({"epochs": epochs})

        # Scale the values to 0.0 to 1.0
        train_images = dataset.images / 255.0

        # Reshape for feeding into the model
        train_images = train_images.reshape(train_images.shape[0], 28, 28, 1)

        # Define the model architecture.
        model = keras.Sequential(
            [
                keras.layers.Conv2D(
                    input_shape=(28, 28, 1),
                    filters=8,
                    kernel_size=3,
                    strides=2,
                    activation="relu",
                    name="Conv1",
                ),
                keras.layers.Flatten(),
                keras.layers.Dense(10, name="Dense"),
            ]
        )
        model.summary()

        # Fit the model to the training data.
        model.compile(
            optimizer="adam",
            loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
            metrics=[keras.metrics.SparseCategoricalAccuracy()],
        )
        model.fit(train_images, dataset.labels, epochs=epochs)

        # Store model in MLflow.
        mlflow.keras.log_model(model, artifact_path=mlflow_artifact_path)

        return TrainResult(
            mlflow_run_id=run.info.run_id,
            mlflow_artifact_path=mlflow_artifact_path,
        )


# def evaluate_model():
