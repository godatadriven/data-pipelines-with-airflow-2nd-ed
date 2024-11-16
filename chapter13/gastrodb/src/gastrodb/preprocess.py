from typing import List
import pandas as pd
from .utils import get_minio_fs

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from weaviate.util import generate_uuid5


def append_content(files_to_process: List[str], path:str, content_col:str) -> pd.DataFrame:

    fs, base_path = get_minio_fs(f"{path}/raw")
    content = []    

    for file in files_to_process:

        filename = file.split("/")[-1]

        with fs.open(f"{base_path}/{filename}", "rb") as file_:
            content.append({"filename": filename, content_col: file_.read()})

    return pd.DataFrame(content)


def split_content(
        df: pd.DataFrame, 
        content_col:str, 
        chunk_size:int, 
        chunk_overlap:int, 
        separators:List[str]
    ) -> pd.DataFrame:

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap, 
        separators=separators
    )

    df = (
        df
        .assign( 
            doc_chunks = lambda df: df[content_col].apply(lambda x: splitter.split_documents([Document(page_content=x)]))
        )
        .explode("doc_chunks", ignore_index=True)
        .assign( 
            chunk = lambda df: [ chunk.page_content for chunk in df.doc_chunks],
            document_sha = lambda df: [generate_uuid5(file) for file in df.filename],
            chunk_sha = lambda df: [generate_uuid5(file) for file in df.chunk],
        )
        .drop(["doc_chunks",content_col], axis=1)
        .reset_index(drop=True)
        .loc[:, ["filename", "document_sha", "chunk_sha", "chunk"]]
    )

    return df



def clean(df, content_col:str) -> pd.DataFrame:
    
    return df.assign(
        **{content_col: lambda df: 
           df[content_col].astype(str)
           .str.replace("\n", " " )
            .str.strip()
        }
    )
   
   
