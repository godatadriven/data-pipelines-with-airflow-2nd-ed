#!/usr/bin/env bash

function publish_custom_images() {
    echo "==============================================="
    echo "== Build local airflow image                 =="
    echo "==============================================="
    docker build -t manning-airflow/my-airflow:k8s -f Dockerfile .
    echo "==============================================="
    echo "== Tag images for container registry         =="
    echo "==============================================="
    docker tag manning-airflow/my-airflow:k8s localhost:3632/manning-airflow/my-airflow:k8s
    echo "==============================================="
    echo "== Push image to container registry          =="
    echo "==============================================="
    docker push localhost:3632/manning-airflow/my-airflow:k8s
}

publish_custom_images
