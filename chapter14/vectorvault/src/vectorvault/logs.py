
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
    log.warning(f"###### {df.shape}{df_name} ##################################")
    custom_df_log(df, log)



def custom_df_log(df, log:Logger) -> None:
    # Create a list to hold formatted column names
    formatted_columns = []
    
    for col in df.columns:

        formatted_col = (col[:12] + '...') if len(col) > 15 else col
        formatted_columns.append(formatted_col.ljust(15))  # Ensure 15 char space

    # Print the formatted column names with 2 spaces between them
    log.warning('  '.join(formatted_columns))

    # Iterate over each row in the DataFrame
    for index, row in df.iterrows():
        formatted_values = []
        for col in df.columns:
            value = row[col]
            if isinstance(value, str) and len(value) > 15:
                if "uuid" in col.lower():
                    formatted_value =  '...' + value[-12:] 
                else:
                    formatted_value = value[:12] + '...'
            else:
                formatted_value = str(value)
            formatted_values.append(formatted_value.ljust(15))  # Ensure 15 char space

        # Print the formatted row values with 2 spaces between them
        log.warning('  '.join(formatted_values))