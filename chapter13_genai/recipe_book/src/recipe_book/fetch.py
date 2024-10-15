from dataclasses import dataclass
from typing import Tuple

import fsspec

import numpy as np
import numpy.typing as npt
import pandas as pd



def load_file( dataset_path: str):
    fs, base_path = fsspec.core.url_to_fs(dataset_path)

    return cls(
        images=_load_array(fs, base_path + "/images.npy"),
        labels=_load_array(fs, base_path + "/labels.npy"),
    )

def save(self, output_path: str):
    fs, base_path = fsspec.core.url_to_fs(output_path)

    fs.makedirs(base_path, exist_ok=True)

    _write_array(fs, base_path + "/images.npy", self.images)
    _write_array(fs, base_path + "/labels.npy", self.labels)




@dataclass
class Dataset:
    images: npt.NDArray[np.uint8]
    labels: npt.NDArray[np.uint8]

    @classmethod
    def load(cls, dataset_path: str):
        fs, base_path = fsspec.core.url_to_fs(dataset_path)

        return cls(
            images=_load_array(fs, base_path + "/images.npy"),
            labels=_load_array(fs, base_path + "/labels.npy"),
        )

    def save(self, output_path: str):
        fs, base_path = fsspec.core.url_to_fs(output_path)

        fs.makedirs(base_path, exist_ok=True)

        _write_array(fs, base_path + "/images.npy", self.images)
        _write_array(fs, base_path + "/labels.npy", self.labels)


def fetch_datasets() -> Tuple[Dataset, Dataset]:
    # Delay import to speed up CLI.
    import keras

    fashion_mnist = keras.datasets.fashion_mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

    train_dataset = Dataset(images=train_images, labels=train_labels)
    test_dataset = Dataset(images=test_images, labels=test_labels)

    return train_dataset, test_dataset


def load_file(filename:str, path:str) -> pd.DataFrame:
    
    print(path)
    
    fs, base_path = fsspec.core.url_to_fs(path)

    print(base_path, path)

    with fs.open(f"{base_path}.{filename}", "rb") as file_:
        return pd.read_parquet(file_)

def _write_array(fs: fsspec.AbstractFileSystem, path: str, array: npt.NDArray[np.uint8]):
    with fs.open(path, "wb") as file_:
        np.save(file_, array)
