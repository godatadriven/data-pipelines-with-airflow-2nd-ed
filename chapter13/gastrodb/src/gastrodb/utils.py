import fsspec
from typing import Tuple, List
import pandas as pd
from weaviate import WeaviateClient
import weaviate
import os

from weaviate.classes.config import Configure

def get_minio_fs(path: str) -> Tuple[fsspec.spec.AbstractFileSystem, str]:   

    return fsspec.core.url_to_fs(path)

def list_files_from_fs(path: str) -> List[str]:
    try:
        fs, base_path = fsspec.core.url_to_fs(path)
    except FileNotFoundError:
        return []

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


def get_weaviate_client(connection_type:str) -> WeaviateClient:

    if connection_type == "azure":
        headers = {"X-Azure-Api-Key": os.getenv("OPENAI_API_KEY")}
    elif connection_type == "openai_api":
        headers = {"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}

    return weaviate.connect_to_custom(
            http_host='weaviate',
            http_port=os.getenv("WEAVIATE_HOST_PORT_REST"),
            http_secure=False,
            grpc_host='weaviate',
            grpc_port=os.getenv("WEAVIATE_HOST_PORT_GRPC"),
            grpc_secure=False,
            headers=headers,
        )
    

def get_vectorizer_config(embedding_model: str, connection_type:str) -> Configure:

    if connection_type == "azure":

        config =  Configure.NamedVectors.text2vec_azure_openai(
                        name=embedding_model.replace("-", "_"),
                        source_properties=["recipe_name", "chunk"],
                        deployment_id=embedding_model,
                        base_url= os.getenv("AZURE_OPENAI_ENDPOINT"),
                        resource_name= os.getenv("AZURE_OPENAI_RESOURCE_NAME"),
                    )   

    elif connection_type == "openai_api":

        config = Configure.NamedVectors.text2vec_openai(
                            name=embedding_model.replace("-", "_"),
                            source_properties=["recipe_name", "chunk"],
                            model=embedding_model,
                        )

    else:
        raise ValueError(f"Connection type {connection_type} not supported.")

    return config
    
