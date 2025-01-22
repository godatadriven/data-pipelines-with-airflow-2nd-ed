
import streamlit as st
from datetime import date
import json

import fsspec


st.set_page_config(page_title="Upload", page_icon="🔼_", layout="wide")


recipe_name = st.text_input("Recipe Name", placeholder="Enter recipe name", label_visibility="collapsed")

st.markdown("### Ingredients")

ingredients = st.text_area(
    "Ingredients",
    placeholder = "Write your recipe ingredients here",
    height = 200,
    label_visibility="collapsed"
)


st.markdown("### Instructions")
instructions = st.text_area(
    "Instructions",
    placeholder = "Write recipe instructions here",
    height = 200,
    label_visibility="collapsed"
)

upload = st.button("Upload Recipe")

if upload & (recipe_name != "") & (ingredients != "") & (instructions != ""):

    json_data = {
        "name": recipe_name,
        "ingredients": ingredients,
        "instructions": instructions
    }

    ds = date.today().strftime("%Y-%m-%d")

    print(ds)

    dest_path = f"s3://data/{ds}/raw"
    print(dest_path)

    fs, base_path = fsspec.core.url_to_fs(dest_path)

    #upload json data to s3
    with fs.open(f"{base_path}/recipe_name.json", "w") as f:
        json.dumps(json_data)

    st.write("Recipe uploaded successfully")