"""DAG demonstrating the umbrella use case with empty operators."""

import pendulum
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from kubernetes.client import models as k8s


def _tf_version():
    import tensorflow as tf
    print("TensorFlow version:", tf.__version__)

with DAG(
    dag_id="01_dag_dependencies_in_image",
    description="Dag dependencies in custom image example.",
    start_date=pendulum.today("UTC").add(days=-5),
    schedule="@daily",
):
    some_init_task = EmptyOperator(task_id="init")
    version_fail = PythonOperator(task_id="version_celery", python_callable=_tf_version, executor="CeleryExecutor")
    version_k8s = PythonOperator(task_id="version_k8s", python_callable=_tf_version, executor="KubernetesExecutor",
      executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            env=[
                                k8s.V1EnvVar(
                                    name="AIRFLOW__CORE__EXECUTOR",
                                    value="CeleryExecutor,KubernetesExecutor"
                                )
                            ],
                        )
                    ]
                )
            ),
        }
    )
    finish = EmptyOperator(task_id="finish", trigger_rule="one_success")

    # Set dependencies between all tasks
    some_init_task >> [ version_fail, version_k8s ] >> finish
