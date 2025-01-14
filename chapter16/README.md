# Chapter 16

Code accompanying Chapter 16 of the book [Data Pipelines with Apache Airflow](https://www.manning.com/books/data-pipelines-with-apache-airflow).

The chapter explains the different options of deploying Airflow in Kubernetes. For executing these deployment commands a docker compose based Kubernetes cluster is available in this chapters `docker-compose.yml` provided with this repository. To start this cluster setup the following command can be used:

```bash
docker compose up -d
```

!! **This setup requires more resources so it is good to at least give docker 4 CPU and 8GB memory**

## More information

### Kubectl and helm

To work with the kubernetes cluster a separate container is available to execute `kubectl` and `helm` commands against the cluster. It is important to start this container with a so called `login shell` because we need the `kubectl` alias which provides the --server commandline option to connect to the k8s server.

```bash
docker exec -ti chapter16-k3s-cli-1 /bin/bash -l
```

#### K9s or local kubectl as an alternative

You could use [k9s](https://k9scli.io/) or install kubectl locally. To make sure you can connect to the k3s cluster you need to make use of the cluster config (`KUBECONFIG=.k3s/kubeconfig.yaml`).

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

access the webserver at http://localhost:8080 (or http://localhost:8081 if the webserver pod ends up being deployed at the agent node. This can be verified with the `kubectl --namespace airflow get pods -o wide` command). In the rest of this README we refer to the webserver as http://localhost:8080.


### 01 - Overriding the default user

In values/01-user-values.yaml we create a different admin user to have the same login as the other chapters and have a easy introduction in customizing your Airflow deployment

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --set webserver.service.type=LoadBalancer -f /etc/helm/values/01-user-values.yaml
```

You can verify that the Admin user is changed by logging in http://localhost:8080 with airflow/airflow and go to http://localhost:8080/users/userinfo/ to see the changed values.
You can also see that the affected pods (at least the webserver) have been changed (age is more recent)

```bash
kubectl --namespace airflow get pods
```

### 02 - Providing the webserver secret

In values/02-webserversecret-values.yaml we provide our own secret to prevent the UI warning about a non-static secret.

```bash
kubectl create secret generic my-webserver-secret --namespace airflow --from-literal="webserver-secret-key=$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
```

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer -f /etc/helm/values/02-webserversecret-values.yaml
```

You can verify this by logging in http://localhost:8080 with airflow/airflow.

### 03 - Using an external database

In values/03-external-database-values.yaml we configure the deployment to use an external database. This database is already provided in the docker compose file. The connnection info is provided to the helm chart via a kubernetes secret again.

```bash
kubectl create secret generic mydatabase --namespace airflow --from-literal=connection=postgresql://airflow:airflow@postgres:5432/airflow
```

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer -f /etc/helm/values/03-external-database-values.yaml
```

```bash
kubectl delete statefulset airflow-postgresql --namespace airflow
```

You can verify this by logging in http://localhost:8080 with airflow/airflow. (The original admin/admin user is not available anymore)


### 04 - Dag Deployment options

#### 04a - Baking the DAGS in the airflow image

In values/04-dags-in-image-values.yaml we configure the deployment to use an custom container image. This image contains the dag files which are added during building the image. The image was pushed to the registry (available in docker compose) so it can be pulled by the helm deployment.

```bash
# on your local machine
./publish-custom-images.sh
```

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer -f /etc/helm/values/04-dags-in-image-values.yaml
```

Now when you log in http://localhost:8080 with airflow/airflow, you can see the dag `01_dag_in_image` being available.

#### 04b - DAGS in persistent volume

In values/04-dags-in-persistent-vol-values.yaml we configure the deployment to use an persistent volume. This volume contains the dag files and is used by all airflow services.

First we need to create the persistent volume and a volume claim.

```bash
kubectl -n airflow apply -f /etc/helm/values/dag-pvc.yaml
```

Then we can update the deployment to make use of this persistent volume

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer -f /etc/helm/values/04-dags-in-persistent-vol-values.yaml
```

Now when you log in http://localhost:8080 with airflow/airflow, you can see the dags `02_teamA_dag_from_pvc` and `02_teamB_dag_from_pvc` being available.

#### 04c - DAGS in a git repository

In values/04-dags-in-git-values.yaml we configure the deployment to use a git sync sidecar container to sync the dags from a git repository. For this example we use the dags from chapter02.

We can update the deployment to make use of this method

```bash
helm upgrade --install airflow apache-airflow/airflow --namespace airflow --create-namespace --set webserver.service.type=LoadBalancer -f /etc/helm/values/04-dags-in-git-values.yaml
```

Now when you log in http://localhost:8080 with airflow/airflow, you can see the dags `02_teamA_dag_from_pvc` and `02_teamB_dag_from_pvc` being available.
