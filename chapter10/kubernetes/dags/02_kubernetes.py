import os
from datetime import datetime

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from kubernetes.client import models as k8s

with DAG(
    dag_id="02_kubernetes",
    description="Fetches ratings from the Movielens API using kubernetes.",
    start_date=datetime(2023, 1, 1),
    end_date=datetime(2023, 1, 3),
    schedule="@daily",
    default_args={"depends_on_past": True},
    max_active_runs=1,
) as dag:
    volume_claim = k8s.V1PersistentVolumeClaimVolumeSource(claim_name="data-volume")
    volume = k8s.V1Volume(name="data-volume", persistent_volume_claim=volume_claim)

    volume_mount = k8s.V1VolumeMount(name="data-volume", mount_path="/data", sub_path=None, read_only=False)

    fetch_ratings = KubernetesPodOperator(
        task_id="fetch_ratings",
        image="registry:5000/manning-airflow/movielens-fetch:k8s",
        cmds=["fetch-ratings"],
        arguments=[
            "--start_date",
            "{{data_interval_start | ds}}",
            "--end_date",
            "{{data_interval_end | ds}}",
            "--output_path",
            "/data/ratings/{{data_interval_start | ds}}.json",
            "--user",
            os.environ["MOVIELENS_USER"],
            "--password",
            os.environ["MOVIELENS_PASSWORD"],
            "--host",
            os.environ["MOVIELENS_HOST"],
        ],
        namespace="airflow",
        name="fetch-ratings",
        config_file="/opt/airflow/kubeconfig.yaml",
        in_cluster=False,
        volumes=[volume],
        volume_mounts=[volume_mount],
        image_pull_policy="IfNotPresent",
        is_delete_operator_pod=True,
    )

    rank_movies = KubernetesPodOperator(
        task_id="rank_movies",
        image="registry:5000/manning-airflow/movielens-rank:k8s",
        cmds=["rank-movies"],
        arguments=[
            "--input_path",
            "/data/ratings/{{data_interval_start | ds}}.json",
            "--output_path",
            "/data/rankings/{{data_interval_start | ds}}.csv",
        ],
        namespace="airflow",
        name="rank-movies",
        config_file="/opt/airflow/kubeconfig.yaml",
        in_cluster=False,
        volumes=[volume],
        volume_mounts=[volume_mount],
        image_pull_policy="IfNotPresent",
        is_delete_operator_pod=True,
    )

    fetch_ratings >> rank_movies
