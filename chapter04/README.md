# Chapter 4

Code accompanying Chapter 4 of the book 'Data pipelines with Apache Airflow'.

## Contents

This code example contains the following DAGs:

TODO

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

## events-api

This chapter includes an API that is used in the code examples. This API is called the `events-api` and is used in the example DAGs. If you want to send requests
to this API outside Airflow DAGs, you can run:
```bash
curl http://events-api:8081/events/latest
```
if you're inside the Docker-compose environment. If you want to run this from your local system, use:
```bash
curl http://localhost:8081/events/latest
```
