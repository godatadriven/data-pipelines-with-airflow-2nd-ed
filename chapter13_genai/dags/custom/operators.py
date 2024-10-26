from airflow.models import BaseOperator
from weaviate.classes.config import Configure, Property, DataType

from typing import List, Optional

from custom.hooks import WeaviateHook

import logging


log = logging.getLogger(__name__)

class WeaviateCreateCollectionOperator(BaseOperator):
    """
    Operator that creates a collection in Weaviate.

    Parameters
    ----------
    conn_id : str
        Id of the connection to use to connect to the Weaviate API. 
    collection_name : str
        Name of the collection to create.
    name_of_configuration: str
        Name of the vector configuration.
    metadata_fields : list[str]
        List of properties to vectorize. Default is None, which means all text properties are vectorized.
    embedding_model : str
        Name of the embedding model to use. It needs to be available as an Azure OpenAI endpoint.
        By default, it uses text-embedding-3-large.
    debug : bool
        If True, deletes the collection if it already exists. Default is False.
        This is useful for debugging purposes.
    """

    def __init__(
        self,
        conn_id: str,
        collection_name: str,
        name_of_configuration: str,
        metadata_fields :  Optional[List[str]] = None,
        embedding_model: str="text-embedding-3-large",
        debug: bool =False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._conn_id = conn_id
        self._collection_name = collection_name
        self._name_of_configuration = name_of_configuration
        self._metadata_fields = metadata_fields
        self._embedding_model = embedding_model
        self._debug = debug

    def execute(self, context):

        hook = WeaviateHook(self._conn_id)

        client =hook.get_weaviate_connection()

        existing_collections = [item.lower() for item in list(client.collections.list_all().keys())]

        if self._debug:
            log.info(f"Deleting {self._collection_name} collection.")
            client.collections.delete(self._collection_name)


        print(self._collection_name.lower(), existing_collections)
        if self._collection_name.lower() in existing_collections:
            log.info(f"Collection {self._collection_name} exists.")


        else:
            log.info(f"Collection {self._collection_name} does not exist yet.")  
            
            collection = client.collections.create(
                self._collection_name,
                vectorizer_config=[
                    Configure.NamedVectors.text2vec_azure_openai(
                        name= self._name_of_configuration,
                        source_properties= self._metadata_fields,
                        base_url= hook.get_azure_openai_endpoint(),
                        resource_name= hook.get_azure_openai_resource_name(),
                        deployment_id=self._embedding_model,
                    )    
                ],
                properties=[
                    Property(name="filename", data_type=DataType.TEXT),
                    Property(name="chunk", data_type=DataType.TEXT),
                    Property(name="chunk_sha", data_type=DataType.UUID, skip_vectorization=True),
                ]
   
            )

            log.info(f"Collection {self._collection_name} created.")    

            log.info(collection.config.get().to_dict())

        client.close()

