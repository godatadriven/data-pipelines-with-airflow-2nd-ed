# Chapter 10 - Kubernetes

Code accompanying the Kubernetes part of Chapter 10 from the book 'Data pipelines with Apache Airflow'.

## Contents

This directory contains the Kubernetes equivalent of the recommender system demonstrated in the chapter10_1_docker example.

### Usage

First, you need to make sure you have a Kubernetes cluster set up and can run commands on the cluster using kubectl.

For your convenience we have set one up inside docker-compose so the way to get things running is similar to the other chapters. Feel free to use another way of setting up a k8s cluster like `minikube`, `docker-desktop` or a cloud service of your choice.

```
# First build the used images and make them available for the k8s service
./setup_local_image_registry.sh
docker compose up -d
```

In a separate terminal you can try the `kubectl cluster-info` command mentioned in the book to see if it connects to your k8s cluster correctly. If you want to run it from your own machine make sure you have the KUBECONFIG env var set correctly (see .env)
For you convenience there is a docker container available where you can exec into to have kubectl available

```
docker exec -ti kubernetes-k3s-cli-1 /bin/bash
```

Once you have this in place, you can start creating the required namespace and resources:

```
kubectl create namespace airflow
kubectl -n airflow apply -f /resources/data-volume.yml
kubectl -n airflow apply -f /resources/api.yml
```

You can test if the API is running properly using:

```
kubectl -n airflow port-forward --address 0.0.0.0 svc/movielens 8081:8081
```

and opening http://localhost:8081 in the browser (this should show a hello world page from the API).

Once this initial setup is complete, you should be able to run the Kubernetes DAG from within Airflow

If you run into issues, you can lookup the status of the different Kubernetes pods using:

```
kubectl --namespace airflow get pods
```

For failing pods, you can examine their status using:

```
kubectl --namespace describe pod [NAME-OF-POD]
```

You can tear down any used resources with:

```
docker compose down -v
```
