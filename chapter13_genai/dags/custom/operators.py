import json
import os

from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

from custom.hooks import WeaviateHook

import logging

log = logging.getLogger(__name__)


class CreateWeaviateCollectionOperator(BaseOperator):
    """
    Operator that creates a collection in Weaviate.

    Parameters
    ----------
    conn_id : str
        ID of the connection to use to connect to the Weaviate API. 
    collection_name : str
        Name of the collection to create.

    """

    @apply_defaults
    def __init__(
        self,
        conn_id,
        collection_name,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self._conn_id = conn_id
        self._collection_name = collection_name


    def execute(self, context):

        client = WeaviateHook(self._conn_id).get_conn()

        existing_collections = [item.lower() for item in list(client.collections.list_all().keys())]

        if self._collection_name.lower() in existing_collections:
            log.info(f"Collection {self._collection_name} exists.")
        else:
            log.info(f"Collection {self._collection_name} does not exist yet.")  
            client.collections.create(name= self._collection_name)
            log.info(f"Collection {self._collection_name} created.")    

        client.close()