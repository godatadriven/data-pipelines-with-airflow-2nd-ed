"""DAG demonstrating the umbrella use case with empty operators."""

import pendulum
from airflow.exceptions import AirflowException
from airflow.providers.standard.operators.empty import EmptyOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG
from airflow.timetables.trigger import CronTriggerTimetable
from kubernetes.client import models as k8s


def _tf_version():
    import tensorflow as tf
    if tf.__version__ == "2.19.0":
        print("Found correct TensorFlow version:", tf.__version__)
    else:
        raise AirflowException(f"Found Incorrect TensorFlow version: { tf.__version__ }, expected 2.19.0")

def _tf_version_old():
    import tensorflow as tf
    if tf.__version__ == "2.18.1":
        print("Found correct TensorFlow version:", tf.__version__)
    else:
        raise AirflowException(f"Found Incorrect TensorFlow version: { tf.__version__ }, expected 2.18.1")


with DAG(
    dag_id="01_dag_dependencies_in_image",
    description="Dag dependencies in custom image example.",
    start_date=pendulum.today("UTC").add(days=-5),
    schedule=CronTriggerTimetable("@daily", timezone="UTC"),
):
    some_init_task = EmptyOperator(task_id="init")
    version_fail = PythonOperator(
        task_id="version_celery",
        python_callable=_tf_version,
        executor="CeleryExecutor"
    )
    version_k8s = PythonOperator(
        task_id="version_k8s",
        python_callable=_tf_version,
        executor="KubernetesExecutor",
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
    version_k8s_old = PythonOperator(
        task_id="version_k8s_old",
        python_callable=_tf_version_old,
        executor="KubernetesExecutor",
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            image="registry:5000/manning-airflow/airflow-executors-tf-old:k8s",
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
    some_init_task >> [ version_fail, version_k8s, version_k8s_old ] >> finish
