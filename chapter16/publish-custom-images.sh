#!/usr/bin/env bash

function publish_custom_images() {
    echo "==============================================="
    echo "== Build local airflow image(s)              =="
    echo "==============================================="
    docker build -t manning-airflow/my-airflow:k8s -f Dockerfile.dags-in-image .
    docker build -t manning-airflow/airflow-deps:k8s -f Dockerfile.deps-in-image .
    echo "==============================================="
    echo "== Tag images for container registry         =="
    echo "==============================================="
    docker tag manning-airflow/my-airflow:k8s localhost:3632/manning-airflow/my-airflow:k8s
    docker tag manning-airflow/airflow-deps:k8s localhost:3632/manning-airflow/airflow-deps:k8s
    echo "==============================================="
    echo "== Push image(s) to container registry       =="
    echo "==============================================="
    docker push localhost:3632/manning-airflow/my-airflow:k8s
    docker push localhost:3632/manning-airflow/airflow-deps:k8s
}

publish_custom_images
