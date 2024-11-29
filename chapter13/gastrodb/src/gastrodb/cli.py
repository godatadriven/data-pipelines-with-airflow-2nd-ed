import typer
import dotenv
import os
import json

from .preprocess import append_content, clean , split_content
from .utils import (
    list_files_from_fs, 
    save_df_in_minio, 
    upload_file_to_minio,
    load_parquet_from_minio,
    get_weaviate_client,
    get_vectorizer_config,
)

from gastrodb.logs import (
    log_header,
    log_files_uploaded,
    log_dataframe,

)

import logging
from weaviate.classes.config import Property, DataType
from weaviate.classes.query import Filter

dotenv.load_dotenv()
app = typer.Typer()
log = logging.getLogger(__name__)

log_header(log)

@app.command()
def upload(ds: str)-> None:

    source_path = f"/app/sample_recipes/{ds}"
    dest_path = f"s3://data/{ds}/raw"

    files_to_upload = list_files_from_fs(source_path)

    for file in files_to_upload:
        upload_file_to_minio(file, dest_path)

    log_files_uploaded(log, files_to_upload , dest_path)


@app.command()
def preprocess(path: str) -> None:

    files_to_process = list_files_from_fs(f"{path}/raw")

    df = (
        append_content(files_to_process, path, content_col="recipe")
        .pipe(clean, content_col="recipe")
    )
 
    save_df_in_minio(df, path, "preprocessed")

@app.command()
def compare(path: str, collection_name:str, connection_type:str) -> None:

    df = (
        load_parquet_from_minio( "splitted", path)
        .assign(regime=None)
        .reset_index(drop=True)
    )

    log_dataframe(log, df, "Source Dataframe from preprocessed")

    for recipe in df.recipe_uuid.unique():

        recipes = df[df.recipe_uuid == recipe]

        response = (
            get_weaviate_client(connection_type)
            .collections
            .get(name=collection_name)
            .query
            .fetch_objects(filters=Filter.by_property("recipe_uuid").equal(recipe))
        )

        keys_in_db = [str(object.uuid) for object in response.objects]

        if len(keys_in_db) == 0:
            df.loc[recipes.index, "regime"] = "create"
        elif set(recipes.chunk_uuid) != set(keys_in_db):
            df.loc[recipes.index, "regime"] = "update"

    df  = df.dropna(subset="regime")

    save_df_in_minio(df, path, "compared")
    log_dataframe(log, df, "Saved compared dataframe ")


@app.command()
def delete(path: str, collection_name:str, connection_type:str) -> None:

    df = (
        load_parquet_from_minio( "compared", path)
        .loc[lambda df: df.regime == "update"]
    )

    log_dataframe(log, df, "Chunks to be deleted")

    log.warning(f"{len(df)} recipes to be deleted from {collection_name}")

    if len(df) > 0:

        client = get_weaviate_client(connection_type)
        
        (
            client
            .collections.get(name=collection_name)
            .data.delete_many(
                where=Filter.by_id().contains_any(df.chunk_uuid.unique()) 
            )
        )

        client.close()



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
        connection_type:str, 
    ) -> None:

    client = get_weaviate_client(connection_type)

    collections = list(client.collections.list_all().keys())
    existing_collections = [item.lower() for item in collections]

    if collection_name.lower() in existing_collections:
        log.warning(f"Collection {collection_name} exists.")
        client.close()
        return

    log.warning(f"Collection {collection_name} does not exist yet...creating it.")  
    
    collection = client.collections.create(
        name = collection_name,
        vectorizer_config=[get_vectorizer_config(embedding_model, connection_type)],
        properties=[
            Property(name="recipe_uuid", data_type=DataType.UUID, skip_vectorization=True),
            Property(name="recipe_name", data_type=DataType.TEXT),
            Property(name="chunk_uuid", data_type=DataType.UUID, skip_vectorization=True),
            Property(name="chunk", data_type=DataType.TEXT),
        ]

    )

    log.warning(f"Collection {collection_name} created.")    
    log.warning(collection.config.get().to_dict())

    client.close()

@app.command()
def save(collection_name:str, path: str, connection_type:str) -> None:

    client = get_weaviate_client(connection_type)

    source_objects = json.loads( 
        load_parquet_from_minio( "compared", path).drop(columns=["regime"])
        .to_json(orient="records")
    ) 

    if len(source_objects) == 0:
        log.warning("No objects to save")
        return
    
    collection = client.collections.get(collection_name)

    failed_objects = []
    with collection.batch.dynamic() as batch:
        for object in source_objects:
            batch.add_object(
                properties=object,
                uuid=object["chunk_uuid"],
            )

        if failed_objects:
            failed_objects = failed_objects.append(collection.batch.failed_objects)

    if len(failed_objects) > 0:
        log.error(failed_objects)
        raise ValueError("Failed to save {len(failed_objects)} objects.")

    client.close()

if __name__ == "__main__":
    app()
