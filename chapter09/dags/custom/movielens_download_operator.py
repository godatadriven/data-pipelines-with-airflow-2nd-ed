import json

from airflow.models import BaseOperator

from .movielens_hook import MovielensHook


class MovielensDownloadOperator(BaseOperator):
    template_fields = ("_start_date", "_end_date", "_output_path")

    def __init__(
            self,
            conn_id,
            start_date,
            end_date,
            output_path,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self._conn_id = conn_id
        self._start_date = start_date
        self._end_date = end_date
        self._output_path = output_path

    def execute(self, context):
        with MovielensHook(self._conn_id) as hook:
            ratings = list(hook.get_ratings(
                start_date=self._start_date,
                end_date=self._end_date,
            ))

        with open(self._output_path, "w") as f:
            f.write(json.dumps(ratings))
