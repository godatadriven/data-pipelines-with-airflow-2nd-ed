from typing import List
import pandas as pd
from vectorvault.utils import load_json_from_minio
from weaviate.util import generate_uuid5


def create_chunks(files_to_process: List[str], path:str) -> pd.DataFrame:
    
    chunks = []
    for file in files_to_process:

        recipe_name = file.replace(".json","").split("/")[-1]
        data = load_json_from_minio(recipe_name, path)

        ingredients = data.get('ingredients', 'No ingredients found')
        instructions = data.get('instructions', 'No instructions found')
        
        chunks.append({"recipe_name": recipe_name, "chunk": f"{recipe_name} \n Ingredients: {ingredients}"})
        chunks.append({"recipe_name": recipe_name, "chunk": f"{recipe_name} \n Instructions: {instructions}"})

    return pd.DataFrame(chunks)


def assign_uuids(df: pd.DataFrame) -> pd.DataFrame:

    return (
        df
        .assign(
            chunk = lambda df: df.chunk.astype(str).str.strip(),
            recipe_name = lambda df: df.recipe_name.astype(str).str.strip(),
            recipe_uuid = lambda df: [generate_uuid5(file) for file in df.recipe_name],
            chunk_uuid = lambda df: [generate_uuid5(file) for file in df.chunk],
        )
        .reset_index(drop=True)
    )

