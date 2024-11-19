
from logging import Logger
from typing import List
import pandas as pd

def log_header(log:Logger) -> None:
    
    log.warning(r"""  
                 _                 _ _     
                | |               | | |    
  __ _  __ _ ___| |_ _ __ ___   __| | |__  
 / _` |/ _` / __| __| '__/ _ \ / _` | '_ \ 
| (_| | (_| \__ | |_| | | (_) | (_| | |_) |
 \__, |\__,_|___/\__|_|  \___/ \__,_|_.__/ 
  __/ |                                    
 |___/                                     
""")
    

def log_files_uploaded(log:Logger, files: List[str], dest_path:str) -> None:
    log.warning("")
    log.warning("")
    log.warning(f"######  Upload files to minio ##################################")
    log.warning(f"    {len(files)} files  uploaded to {dest_path}")

    for file in files:
        log.warning(f"     - {file}")


def log_dataframe(log:Logger, df:pd.DataFrame, df_name:str) -> None:
    log.warning("")
    log.warning("")
    log.warning(f"###### {df.shape}{df_name} ##################################")
    log.warning(df.head(10))
