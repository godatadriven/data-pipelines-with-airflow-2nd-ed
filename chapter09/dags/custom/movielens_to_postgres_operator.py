from airflow.models import BaseOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook

from .movielens_hook import MovielensHook


class MovielensToPostgresOperator(BaseOperator):
    template_fields = ("_start_date", "_end_date", "_insert_query")

    def __init__(
            self,
            movielens_conn_id,
            start_date,
            end_date,
            postgres_conn_id,
            insert_query,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._movielens_conn_id = movielens_conn_id
        self._start_date = start_date
        self._end_date = end_date
        self._postgres_conn_id = postgres_conn_id
        self._insert_query = insert_query

    def execute(self, context):
        with MovielensHook(self._movielens_conn_id) as movielens_hook:
            ratings = list(movielens_hook.get_ratings(
                start_date=self._start_date,
                end_date=self._end_date),
            )

        postgres_hook = PostgresHook(
            postgres_conn_id=self._postgres_conn_id
        )
        insert_queries = [
            self._insert_query.format(",".join([str(_[1]) for _ in sorted(rating.items())]))
            for rating in ratings
        ]
        postgres_hook.run(insert_queries)
