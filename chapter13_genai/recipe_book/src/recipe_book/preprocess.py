from typing import List
import pandas as pd
from .utils import get_minio_fs

import re

def append_content(files_to_process: List[str], path:str) -> pd.DataFrame:

    fs, base_path = get_minio_fs(f"{path}/raw")
    content = []    

    for file in files_to_process:

        filename = file.split("/")[-1]

        with fs.open(f"{base_path}/{filename}", "rb") as file_:
            content.append({"filename": filename, "chunk": file_.read()})

    return pd.DataFrame(content)


def clean(df, content_col:str) -> pd.DataFrame:
    
    return df.assign(
        **{content_col: lambda df: 
           df[content_col].astype(str)
           .str.replace("\n", " " )
            .str.strip()
        }
    )
   
   
