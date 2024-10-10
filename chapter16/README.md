# Chapter 16

Code accompanying Chapter 16 of the book [Data Pipelines with Apache Airflow](https://www.manning.com/books/data-pipelines-with-apache-airflow).

The chapter explains the different options of deploying Airflow in Kubernetes. For executing these deployment commands a docker compose based Kubernetes cluster is available in this chapters `docker-compose.yml` provided with this repository. To start this cluster setup the following command can be used:

```bash
docker compose up -d
```

!! **This setup requires more resources so it is good to at least give docker 4 CPU and 8GB memory**

## More information

### Kubectl and helm

To work with the kubernetes cluster a separate container is available to execute `kubectl` and `helm` commands against the cluster

```bash
docker exec -ti chapter16-k3s-cli-1 /bin/bash
```

#### K9s or local kubectl as an alternative

You could use [k9s](https://k9scli.io/) or install kubectl locally. To make sure you can connect to the k3s cluster you need to make sure the k3s-server hostname is known locally (add `127.0.0.1 k3s-server` to your hosts file) and you need to use the cluster config (`KUBECONFIG=.k3s/kubeconfig.yaml`)

### Deployment of default airflow in K8S

Inside the k3s-cli container we can deploy airflow with the following commands:

```bash
/enable-external-dns # make sure the other docker services can be reached from within the k3s cluster
helm repo add apache-airflow https://airflow.apache.org
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer
```

to verify the running services/pods we can check with the following command:

```bash
kubectl --namespace airflow get pods
```

access the webserver at http://localhost:8080
