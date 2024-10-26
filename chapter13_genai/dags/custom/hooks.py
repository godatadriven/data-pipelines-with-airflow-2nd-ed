import requests
from airflow.hooks.base import BaseHook
from airflow.models.connection import Connection

import weaviate
from weaviate import WeaviateClient
from weaviate.auth import Auth
from weaviate.auth import AuthCredentials
from weaviate.classes.init import AdditionalConfig, Timeout

from typing import  Any
import logging

log = logging.getLogger(__name__)


class WeaviateHook(BaseHook):
    """
    Hook for Weviate.

    Abstracts details of connection to Weaviate.

    Parameters
    ----------
    conn_id : str
        ID of the connection to use to connect to the weaviate API.\
        
    """

    def __init__(
            self,        
            conn_id: str,
            *args: Any,
            **kwargs: Any, 
        ) -> None:
        super().__init__(*args, **kwargs)
        self.conn_id = conn_id
        self.airflow_connection = Connection.get_connection_from_secrets(conn_id)


    def get_azure_openai_endpoint(self) -> str:
        return (
            self.airflow_connection
            .extra_dejson
            .get("additional_headers", {})
            .get("AZURE_ENDPOINT", "")
        )
    
    def get_azure_openai_resource_name(self) -> str:
        return (
            self.airflow_connection
            .extra_dejson
            .get("additional_headers", {})
            .get("AZURE_RESOURCE_NAME", "")
        )
    
    def get_weaviate_connection(self) -> WeaviateClient:
        extras = self.airflow_connection.extra_dejson
        http_secure = extras.pop("http_secure", False)
        grpc_secure = extras.pop("grpc_secure", False)

        return weaviate.connect_to_custom(
            http_host=self.airflow_connection.host,
            http_port=self.airflow_connection.port,
            http_secure=http_secure,
            grpc_host=extras.pop("grpc_host",""),
            grpc_port=extras.pop("grpc_port",50051),
            grpc_secure=grpc_secure,
            headers=extras.pop("additional_headers", {}),
        )


