import typer
import dotenv
import weaviate
import os
import json

from .preprocess import append_content, clean
from .utils import (
    list_files_from_fs, 
    save_df_in_minio, 
    upload_file_to_minio,
    load_parquet_from_minio,
)

import logging
from weaviate.util import generate_uuid5


dotenv.load_dotenv()
app = typer.Typer()
log = logging.getLogger(__name__)


@app.command()
def upload(source_path: str, dest_path: str):

    files_to_upload = list_files_from_fs(source_path)

    for file in files_to_upload:
        upload_file_to_minio(file, dest_path)


@app.command()
def preprocess(path: str) -> None:

    files_to_process = list_files_from_fs(f"{path}/raw")

    df = (
        append_content(files_to_process, path)
        .pipe(clean, content_col="chunk")
        .assign( 
            document_sha = lambda df: [generate_uuid5(file) for file in df.filename],
            chunk_sha = lambda df: [generate_uuid5(file) for file in df.chunk],
        )
        .reset_index(drop=True)
        .loc[:, ["filename", "document_sha", "chunk_sha", "chunk"]]
    )
 
    save_df_in_minio(df, path, "preprocessed")


@app.command()
def save(collection_name:str, path: str) -> None:

    client = weaviate.connect_to_custom(
            http_host='weaviate',
            http_port=os.getenv("WEAVIATE_HOST_PORT_REST"),
            http_secure=False,
            grpc_host='weaviate',
            grpc_port=os.getenv("WEAVIATE_HOST_PORT_GRPC"),
            grpc_secure=False,
            headers={
                 "X-Azure-Api-Key": os.getenv("X-Azure-Api-Key"),
            }
        )
    
    source_objects = json.loads( 
        load_parquet_from_minio( "preprocessed", path)
        .to_json(orient="records")
    ) 
    
    collection = client.collections.get(collection_name)

    with collection.batch.dynamic() as batch:
        for object in source_objects:

            batch.add_object(
                properties=object,
                uuid=object["chunk_sha"],
            )

    client.close()
if __name__ == "__main__":
    app()
