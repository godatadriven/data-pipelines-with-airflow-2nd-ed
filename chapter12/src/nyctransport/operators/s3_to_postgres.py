import logging
from typing import Callable, Dict

import pandas as pd
from airflow.hooks.base import BaseHook
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.sdk import BaseOperator
from airflow.utils.context import Context
from minio import Minio
from sqlalchemy import create_engine


class MinioPandasToPostgres(BaseOperator):
    template_fields = ("_minio_key",)
    ui_color = "#705B74"
    ui_fgcolor = "#8FA48B"

    def __init__(
        self,
        minio_conn_id,
        minio_bucket,
        minio_key,
        pandas_read_callable,
        postgres_conn_id,
        postgres_table,
        read_callable_kwargs: Dict = None,
        pre_read_transform: Callable = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._minio_conn_id = minio_conn_id
        self._minio_bucket = minio_bucket
        self._minio_key = minio_key
        self._pandas_read_callable = pandas_read_callable
        self._postgres_conn_id = postgres_conn_id
        self._postgres_table = postgres_table
        self._read_callable_kwargs = read_callable_kwargs or {}
        self._pre_read_transform = pre_read_transform

    def execute(self, context:Context):
        conn = BaseHook.get_connection(conn_id=self._minio_conn_id)
        minio_client = Minio(
            conn.extra_dejson["endpoint_url"].split("://")[1],
            access_key=conn.login,
            secret_key=conn.password,
            secure=False,
        )

        logging.info("Reading object: %s/%s.", self._minio_bucket, self._minio_key)
        obj = minio_client.get_object(bucket_name=self._minio_bucket, object_name=self._minio_key)
        if self._pre_read_transform:
            obj = self._pre_read_transform(obj)

        df = self._pandas_read_callable(obj, **self._read_callable_kwargs)
        df["airflow_execution_date"] = pd.Timestamp(context["data_interval_start"].timestamp(), unit="s")
        logging.info("Read DataFrame with shape: %s.", df.shape)

        engine = create_engine(PostgresHook(postgres_conn_id=self._postgres_conn_id).get_uri())
        with engine.begin() as conn:
            conn.execute(
                f"DELETE FROM {self._postgres_table} "
                f"WHERE airflow_execution_date='{context['data_interval_start']}';"
            )
            df.to_sql(self._postgres_table, con=conn, index=False, if_exists="append")

        logging.info("Wrote DataFrame to %s.", self._postgres_table)
