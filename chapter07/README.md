# Chapter 7

Code accompanying Chapter 7 of the book [Data Pipelines with Apache Airflow](https://www.manning.com/books/data-pipelines-with-apache-airflow).

## Contents

This folder contains DAGs from Chapter 7.

## Usage

To get started with the code examples, start Airflow with Docker Compose with the following command:

```bash
docker compose up -d
```

The webserver initializes a few things, so wait for a few seconds, and you should be able to access the
Airflow webserver at http://localhost:8080.

To stop running the examples, run the following command:

```bash
docker compose down -v
```

To run the Kafka example DAG:
1. Turn the DAG on
2. Bash into the Kafka container:
   ```bash
   docker exec -it chapter07-kafka-1 /bin/bash
   ```
3. Run the CLI producer:
   ```bash
   /opt/kafka/bin/kafka-console-producer.sh --topic events --bootstrap-server localhost:9092
   ```
   Send a message when `>` appears. This will trigger the `12_kafka_trigger` DAG to run.
