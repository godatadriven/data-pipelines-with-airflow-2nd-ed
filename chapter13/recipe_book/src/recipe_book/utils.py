import fsspec
from typing import Tuple, List
import pandas as pd

def get_minio_fs(path: str) -> Tuple[fsspec.spec.AbstractFileSystem, str]:   

    return fsspec.core.url_to_fs(path)

def list_files_from_fs(path: str) -> List[str]:

    fs, base_path = fsspec.core.url_to_fs(path)

    return fs.ls(base_path)


def save_df_in_minio(df: pd.DataFrame, dest_path: str, filename:str) -> None:

    fs, base_path = get_minio_fs(dest_path)

    with fs.open(f"{base_path}/{filename}.parquet", "wb") as file_:
        df.to_parquet(file_)

def load_parquet_from_minio(filename:str, path:str) -> pd.DataFrame:

    fs, base_path = get_minio_fs(path)  

    with fs.open(f"{base_path}/{filename}.parquet", "rb") as file_:        
        return pd.read_parquet(file_)


def upload_file_to_minio(source_path: str, dest_path: str) -> None:

    filename = source_path.split("/")[-1]

    fs, base_path = fsspec.core.url_to_fs(dest_path)

    with open(source_path , 'rb') as f:
        fs.pipe(f"{base_path}/{filename}", f.read())
