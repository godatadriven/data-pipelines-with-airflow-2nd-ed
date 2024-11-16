import typer
import dotenv
import weaviate
import os
import json

from .preprocess import append_content, clean , split_content
from .utils import (
    list_files_from_fs, 
    save_df_in_minio, 
    upload_file_to_minio,
    load_parquet_from_minio,
)

import logging

dotenv.load_dotenv()
app = typer.Typer()
log = logging.getLogger(__name__)

@app.command()
def upload(ds: str)-> None:

    source_path = f"/app/sample_recipes/{ds}"
    dest_path = f"s3://data/{{ds}}/raw"

    files_to_upload = list_files_from_fs(source_path)

    for file in files_to_upload:
        upload_file_to_minio(file, dest_path)
    log.info(f"Uploaded {len(files_to_upload)} new recipes on {ds}")
    
@app.command()
def preprocess(path: str) -> None:

    files_to_process = list_files_from_fs(f"{path}/raw")

    df = (
        append_content(files_to_process, path, content_col="recipe")
        .pipe(clean, content_col="recipe")
    )
 
    save_df_in_minio(df, path, "preprocessed")


@app.command()
def split(path: str) -> None:

    df = (
        load_parquet_from_minio( "preprocessed", path)
        .pipe(split_content, content_col="recipe", chunk_size=300, chunk_overlap=100, separators=[" "])
    )

    save_df_in_minio(df, path , "splitted")


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
        load_parquet_from_minio( "splitted", path)
        .to_json(orient="records")
    ) 
    
    collection = client.collections.get(collection_name)

    with collection.batch.dynamic() as batch:
        for object in source_objects:

            batch.add_object(
                properties=object,
                uuid=object["chunk_sha"],
            )

    failed_objects = collection.batch.failed_objects

    if len(failed_objects) > 0:
        log.error(failed_objects)
        raise ValueError("Failed to save {len(failed_objects)} objects.")

    client.close()
if __name__ == "__main__":
    app()
