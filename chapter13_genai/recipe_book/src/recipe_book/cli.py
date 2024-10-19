import typer
import dotenv

from .preprocess import concatenate_content, split_content
from .utils import (
    list_files_from_fs, 
    save_df_in_minio, 
    upload_file_to_minio,
    load_parquet_from_minio,
)


dotenv.load_dotenv()
app = typer.Typer()


@app.command()
def upload(source_path: str, dest_path: str):

    files_to_upload = list_files_from_fs(source_path)

    for file in files_to_upload:
        upload_file_to_minio(file, dest_path)


@app.command()
def preprocess(path: str) -> None:

    files_to_process = list_files_from_fs(f"{path}/raw")

    df = concatenate_content(files_to_process, path)
 
    save_df_in_minio(df, path, "preprocessed")


@app.command()
def split(path: str) -> None:

    sep = ["\n\n", "\n", " ", ""]

    df = (
        load_parquet_from_minio( "preprocessed", path)
        .pipe(split_content, chunk_size=500, chunk_overlap=100, separators=sep)
    )

    save_df_in_minio(df, path , "splitted")



if __name__ == "__main__":
    app()
