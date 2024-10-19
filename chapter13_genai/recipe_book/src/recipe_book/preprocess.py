
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from weaviate.util import generate_uuid5

from typing import List
import pandas as pd
from weaviate.util import generate_uuid5
from .utils import get_minio_fs

def concatenate_content(files_to_process: List[str], path:str) -> pd.DataFrame:

    fs, base_path = get_minio_fs(f"{path}/raw")
    content = []    

    for file in files_to_process:

        filename = file.split("/")[-1]

        with fs.open(f"{base_path}/{filename}", "rb") as file_:
            content.append({"filename": filename, "text_content": file_.read()})

    return pd.DataFrame(content)





def split_content(df, chunk_size, chunk_overlap, separators):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        separators=separators
    )

    df = (
        df
        .assign( 
            doc_chunks = lambda df: df["text_content"].apply(lambda x: splitter.split_documents([Document(page_content=x)]))
        )
        .explode("doc_chunks", ignore_index=True)
        .assign( 
            chunk = lambda df: [ chunk.page_content for chunk in df.doc_chunks],
            document_sha = lambda df: [generate_uuid5(file) for file in df.filename],
            chunk_sha = lambda df: [generate_uuid5(file) for file in df.chunk],
        )
        .drop(["doc_chunks","text_content"], axis=1)
        .reset_index(drop=True)
        .loc[:, ["filename", "document_sha", "chunk_sha", "chunk"]]
    )

    return df