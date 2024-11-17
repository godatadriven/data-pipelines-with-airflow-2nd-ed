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
    get_weaviate_client
)

from typing import List, Optional
import logging
from weaviate.classes.config import Configure, Property, DataType

dotenv.load_dotenv()
app = typer.Typer()
log = logging.getLogger(__name__)

@app.command()
def upload(ds: str)-> None:

    source_path = f"/app/sample_recipes/{ds}"
    dest_path = f"s3://data/{ds}/raw"

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
def create(
        collection_name:str,
        embedding_model:str,    
    ) -> None:

    client = get_weaviate_client()

    existing_collections = [item.lower() for item in list(client.collections.list_all().keys())]

    if collection_name.lower() in existing_collections:
        log.info(f"Collection {collection_name} exists.")

    else:
        log.info(f"Collection {collection_name} does not exist yet...creating it.")  
        
        collection = client.collections.create(
            collection_name,
            vectorizer_config=[
                Configure.NamedVectors.text2vec_azure_openai(
                    name= "recipe_vectorizer",
                    source_properties=["filename", "description"],
                    base_url= os.getenv("AZURE_OPENAI_ENDPOINT"),
                    resource_name= os.getenv("AZURE_OPENAI_RESOURCE_NAME"),
                    deployment_id=embedding_model,
                )    
            ],
            properties=[
                Property(name="filename", data_type=DataType.TEXT),
                Property(name="chunk", data_type=DataType.TEXT),
                Property(name="chunk_sha", data_type=DataType.UUID, skip_vectorization=True),
                Property(name="document_sha", data_type=DataType.UUID, skip_vectorization=True)
            ]

        )

        log.info(f"Collection {collection_name} created.")    

        log.info(collection.config.get().to_dict())

    client.close()

@app.command()
def save(collection_name:str, path: str) -> None:

    client = get_weaviate_client()

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
