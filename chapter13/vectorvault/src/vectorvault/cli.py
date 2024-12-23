import typer
import os
import json
import pandas as pd

from vectorvault.utils import (
    list_files_from_fs, 
    save_df_in_minio, 
    upload_file_to_minio,
    load_parquet_from_minio,
    get_weaviate_client,
    get_vectorizer_config,
    load_json_from_minio
)

from vectorvault.logs import log_header, log_files_uploaded, log_dataframe
from vectorvault.etl import create_chunks, assign_uuids


import logging
from weaviate.classes.config import Property, DataType


from weaviate.classes.query import Filter

app = typer.Typer()
log = logging.getLogger(__name__)

log_header(log)

@app.command()
def upload(ds: str)-> None:

    source_path = f"/app/sample_recipes/{ds}"
    dest_path = f"s3://data/{ds}/raw"

    files_to_upload = list_files_from_fs(source_path,extension=".json")

    for file in files_to_upload:
        upload_file_to_minio(file, dest_path)

    if len(files_to_upload) > 0:
        log_files_uploaded(log, files_to_upload , dest_path)
    else:
        raise ValueError("No files to upload")

@app.command()
def preprocess(path:str) -> None:

    files_to_process = list_files_from_fs(path=f"{path}/raw", extension=".json")

    df = (
        create_chunks(files_to_process, f"{path}/raw")
        .pipe(assign_uuids)
    )

    save_df_in_minio(df, path, "preprocessed")

    log_dataframe(log, df, "Processed dataframe")


@app.command()
def create(
        collection_name:str,
        embedding_model:str,  
    ) -> None:

    with get_weaviate_client() as client:
        collections = list(client.collections.list_all().keys())

    existing_collections = [item.lower() for item in collections]

    if collection_name.lower() in existing_collections:
        log.warning(f"Collection {collection_name} exists.")
        return

    log.warning(f"Collection {collection_name} does not exist yet...creating it.")  
    
    with get_weaviate_client() as client:
        collection = client.collections.create(
            name = collection_name,
            vectorizer_config=[get_vectorizer_config(embedding_model)],
            properties=[
                Property(name="recipe_uuid", data_type=DataType.UUID, skip_vectorization=True),
                Property(name="recipe_name", data_type=DataType.TEXT),
                Property(name="chunk_uuid", data_type=DataType.UUID, skip_vectorization=True),
                Property(name="chunk", data_type=DataType.TEXT),
            ]
        )

    log.warning(f"Collection {collection_name} created.")    
    log.warning(collection.config.get().to_dict())


@app.command()
def compare(path: str, collection_name:str) -> None:

    df = (
        load_parquet_from_minio( "preprocessed", path)
        .assign(regime=None)
        .reset_index(drop=True)
    )

    log_dataframe(log, df, "Source Dataframe from preprocessed")

    with get_weaviate_client() as client:

        for recipe_name in df.recipe_name.unique():

            recipes = df[df.recipe_name == recipe_name]
            filter = Filter.by_property("recipe_name").equal(recipe_name)

            response = (
                client
                .collections
                .get(name=collection_name)
                .query
                .fetch_objects(filters=filter)
            )

            keys_in_db = [str(object.uuid) for object in response.objects]

            if len(keys_in_db) == 0:
                df.loc[recipes.index, "regime"] = "create"
            elif set(recipes.chunk_uuid) != set(keys_in_db):
                log.warning(f"Recipe {recipe_name} will be updated")
                df.loc[recipes.index, "regime"] = "update"

    save_df_in_minio(df.dropna(subset="regime"), path, "compared")
    log_dataframe(log, df, "Saved compared dataframe ")


@app.command()
def delete(path: str, collection_name:str) -> None:

    recipes_to_delete = (
        load_parquet_from_minio( "compared", path)
        .loc[lambda df: df.regime == "update"]
        .recipe_name.unique().tolist()
    )

    log.warning(f"{recipes_to_delete} records to be deleted from {collection_name}")

    if len(recipes_to_delete) == 0:
        log.warning("No records to delete")
        return

    with get_weaviate_client() as client:
        
        filter = Filter.by_property("recipe_name").contains_any(recipes_to_delete)

        (
            client
            .collections.get(name=collection_name)
            .data.delete_many(where=filter)
        )

@app.command()
def save(collection_name:str, path: str) -> None:

    source_objects = ( 
        load_parquet_from_minio( "compared", path).drop(columns=["regime"])
        .to_dict(orient="records")
    ) 

    if len(source_objects) == 0:
        log.warning("No objects to save")
        return
    
    with get_weaviate_client() as client:
        collection = client.collections.get(collection_name)

        failed_objects = []
        with collection.batch.dynamic() as batch:
            for object in source_objects:
                batch.add_object(           
                    properties=object,
                    uuid=object["chunk_uuid"],
                )
            
            log.warning(f"Saving {len(source_objects)} objects to {collection_name}")

            if failed_objects:
                failed_objects = failed_objects.append(collection.batch.failed_objects)

        if len(failed_objects) > 0:
            raise ValueError("Failed to save {len(failed_objects)} objects.")


if __name__ == "__main__":
    app()
