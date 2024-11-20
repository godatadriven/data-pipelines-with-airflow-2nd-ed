import weaviate

import streamlit as st
from langchain_openai.chat_models import AzureChatOpenAI  
import os
from langchain_openai import AzureOpenAIEmbeddings
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from pages.utils import PROMPT

import json

st.set_page_config(page_title="Recipe Chat", page_icon="💬", layout="wide")

COLLECTION_NAME = "recipes"


st.title("Mom's Recipe Chat")

col1,col2 = st.columns([5,3])


weaviate_client = weaviate.connect_to_custom(
        http_host='weaviate',
        http_port=os.getenv("WEAVIATE_HOST_PORT_REST"),
        http_secure=False,
        grpc_host='weaviate',
        grpc_port=os.getenv("WEAVIATE_HOST_PORT_GRPC"),
        grpc_secure=False,
        headers={
                "X-Azure-Api-Key": os.getenv("AZURE_OPENAI_API_KEY"),
        }
    )

openai_client = AzureChatOpenAI(
    model_name="gpt-4", 
    deployment_name = "gpt-4",
    api_version="2024-02-01",
)

embeddings = AzureOpenAIEmbeddings(model="text-embedding-3-large")

weaviate_db = WeaviateVectorStore(
    client=weaviate_client, 
    index_name=COLLECTION_NAME, 
    text_key="chunk", 
    embedding=embeddings
)

combine_docs_chain = create_stuff_documents_chain(openai_client, PROMPT)
rag_chain = create_retrieval_chain(weaviate_db.as_retriever(), combine_docs_chain)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.context_documents = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with col1.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if question := st.chat_input("What is up?"):

    col2.empty()
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": question})
    # Display user message in chat message container
    with col1.chat_message("user"):
        st.markdown(question)

    # Display assistant response in chat message container
    with col1.chat_message("assistant"):
        
        output = rag_chain.invoke({
                "input": question,
                "chat_history": [
                    (message["role"], message["content"]) 
                    for message 
                    in st.session_state.messages
                ]
            }
        )

        print(output["answer"])

        response = json.loads(output["answer"])

        st.session_state.context_documents = output["context"]
        
        weaviate_client.close()
    
        st.markdown(response["answer"])

    if response["provided_recipe"]:

        for document in st.session_state.context_documents:
            col2.html(f"<sup>{document.metadata['filename']}</sub>")
            col2.html(f"<sup><sup>{document.metadata['chunk_uuid']}</sup></sup>")
            col2.html(f"<sub><sup>{document.page_content}</sup></sub>")

    st.session_state.messages.append({"role": "assistant", "content": response["answer"]})

