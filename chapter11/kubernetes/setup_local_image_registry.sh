#!/usr/bin/env bash

function publish_local_images() {
    echo "==============================================="
    echo "== Start local docker registry               =="
    echo "==============================================="
    docker run -d \
        -p 5000:5000 \
        -v ./docker-registry-persistence:/var/lib/registry \
        --name registry \
        --rm \
        registry:2
    echo "==============================================="
    echo "== Build local movielens api image           =="
    echo "==============================================="
    docker build -t manning-airflow/movielens-api:k8s -f ../../chapter09/docker/movielens-api/Dockerfile ../../chapter09/docker/movielens-api
    echo "==============================================="
    echo "== Build local movielens fetch image         =="
    echo "==============================================="
    docker build -t manning-airflow/movielens-fetch:k8s -f ../docker/images/movielens-fetch/Dockerfile ../docker/images/movielens-fetch
    echo "==============================================="
    echo "== Build local movielens rank image          =="
    echo "==============================================="
    docker build -t manning-airflow/movielens-rank:k8s -f ../docker/images/movielens-rank/Dockerfile ../docker/images/movielens-rank
    echo "==============================================="
    echo "== Tag images for local registry             =="
    echo "==============================================="
    docker tag manning-airflow/movielens-api:k8s localhost:5000/manning-airflow/movielens-api:k8s
    docker tag manning-airflow/movielens-fetch:k8s localhost:5000/manning-airflow/movielens-fetch:k8s
    docker tag manning-airflow/movielens-rank:k8s localhost:5000/manning-airflow/movielens-rank:k8s
    echo "==============================================="
    echo "== Push image to local registry              =="
    echo "==============================================="
    docker push localhost:5000/manning-airflow/movielens-api:k8s
    docker push localhost:5000/manning-airflow/movielens-fetch:k8s
    docker push localhost:5000/manning-airflow/movielens-rank:k8s
    echo "==============================================="
    echo "== Stop local docker registry                =="
    echo "==============================================="
    docker stop registry
}

publish_local_images
