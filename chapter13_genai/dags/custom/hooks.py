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

    
    @classmethod
    def get_connection(cls, conn_id: str) -> Connection:
        """
        Get connection, given connection id.

        :param conn_id: connection id
        :return: connection
        """
        from airflow.models.connection import Connection

        conn = Connection.get_connection_from_secrets(conn_id)
        log.info("Retrieving connection '%s'", conn.conn_id)
        return conn


    def get_conn(self) -> WeaviateClient:
        conn = self.get_connection(self.conn_id)
        extras = conn.extra_dejson
        http_secure = extras.pop("http_secure", False)
        grpc_secure = extras.pop("grpc_secure", False)

        return weaviate.connect_to_custom(
            http_host=conn.host,
            http_port=conn.port,
            http_secure=http_secure,
            grpc_host=extras.pop("grpc_host",""),
            grpc_port=extras.pop("grpc_port",80),
            grpc_secure=grpc_secure,
            headers=extras.pop("additional_headers", {}),
            auth_credentials=self._extract_auth_credentials(conn),
        )

    def _extract_auth_credentials(self, conn: Connection) -> AuthCredentials:
        extras = conn.extra_dejson
        # previously token was used as api_key(backwards compatibility)
        api_key = extras.get("api_key", None) or extras.get("token", None)
        if api_key:
            return Auth.api_key(api_key=api_key)

        access_token = extras.get("access_token", None)
        if access_token:
            refresh_token = extras.get("refresh_token", None)
            expires_in = extras.get("expires_in", 60)
            return Auth.bearer_token(
                access_token=access_token, expires_in=expires_in, refresh_token=refresh_token
            )

        scope = extras.get("scope", None) or extras.get("oidc_scope", None)
        client_secret = extras.get("client_secret", None)
        if client_secret:
            return Auth.client_credentials(client_secret=client_secret, scope=scope)