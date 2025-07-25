# Chapter 8

Code accompanying Chapter 8 of the book 'Data pipelines with Apache Airflow'.

## Contents

This code example contains the following DAGs:

- chapter8 - Dag illustrating the Sagemaker external connections.
- chapter8 - Small DAG illustrating the postgres-to-s3 operator.

## Preparation

For the 01_aws_hadwritten_digits_classifier the following needs to be prepared:

- Get a AWS ACCES KEY and a AWS SECRET and make sure these are available in the shell where the code is executed
- Create A Sagemaker Execution Role see: https://docs.aws.amazon.com/sagemaker/latest/dg/sagemaker-roles.html. The ARN needs to be made available to the shell.
- Specify the region to use where the role was created and where the DAG will execute its tasks

```sh
export SAGEMAKER_EXEC_ROLE_ARN=
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_REGION=
export AWS_DEFAULT_REGION=
# When SECRET KEY contains forward slash it needs to be urlencoded
export ENCODED_AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY//\//%2F}
```

## Usage

To get started with the code examples, start Airflow in docker using the following command:

```bash
docker compose up -d --build
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

```bash
docker compose down -v
```

## Testing the mnist classifier

To test the Mnist classifier that was made available as a Sagemaker Endpoint the book describes a small api application build with Chalice.

This app can be run locally as follows:

```sh
cd api/classifier
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_REGION=
export AWS_DEFAULT_REGION=
chalice local --port 8000
```

## Executing the airflow test commands

To execute the airflow test commands from the book we need a local environment with the correct python packages

```sh
python3 -m venv .airflowlocal
source .airflowlocal/bin/activate
pip install -r requirements.txt
export AWS_ACCESS_KEY_ID=
export AWS_SECRET_ACCESS_KEY=
export AWS_REGION=
export AWS_DEFAULT_REGION=

airflow tasks test 01_aws_handwritten_digits_classifier create_mnist_bucket 2024-01-01
```
