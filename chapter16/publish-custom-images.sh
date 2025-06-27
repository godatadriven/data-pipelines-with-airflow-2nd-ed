#!/usr/bin/env bash

AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME:-apache/airflow:3.0.2}
function publish_custom_images() {
    echo "==============================================="
    echo "== Build local airflow image(s)              =="
    echo "==============================================="
    docker build --build-arg AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME} -t manning-airflow/my-airflow:k8s -f Dockerfile.dags-in-image .
    docker build --build-arg AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME} -t manning-airflow/airflow-deps:k8s -f Dockerfile.deps-in-image .
    docker build --build-arg AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME} -t manning-airflow/airflow-executors:k8s -f Dockerfile.executors_default_image .
    docker build --build-arg AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME} -t manning-airflow/airflow-executors-tf:k8s -f Dockerfile.executors_tensorflow .
    docker build --build-arg AIRFLOW_IMAGE_NAME=${AIRFLOW_IMAGE_NAME} -t manning-airflow/airflow-executors-tf-old:k8s -f Dockerfile.executors_tensorflow_old .
    echo "==============================================="
    echo "== Tag images for container registry         =="
    echo "==============================================="
    docker tag manning-airflow/my-airflow:k8s localhost:3632/manning-airflow/my-airflow:k8s
    docker tag manning-airflow/airflow-deps:k8s localhost:3632/manning-airflow/airflow-deps:k8s
    docker tag manning-airflow/airflow-executors:k8s localhost:3632/manning-airflow/airflow-executors:k8s
    docker tag manning-airflow/airflow-executors-tf:k8s localhost:3632/manning-airflow/airflow-executors-tf:k8s
    docker tag manning-airflow/airflow-executors-tf-old:k8s localhost:3632/manning-airflow/airflow-executors-tf-old:k8s
    echo "==============================================="
    echo "== Push image(s) to container registry       =="
    echo "==============================================="
    docker push localhost:3632/manning-airflow/my-airflow:k8s
    docker push localhost:3632/manning-airflow/airflow-deps:k8s
    docker push localhost:3632/manning-airflow/airflow-executors:k8s
    docker push localhost:3632/manning-airflow/airflow-executors-tf:k8s
    docker push localhost:3632/manning-airflow/airflow-executors-tf-old:k8s
}

publish_custom_images
