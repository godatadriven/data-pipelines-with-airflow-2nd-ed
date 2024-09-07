# Chapter 9

Code accompanying Chapter 9 of the book 'Data pipelines with Apache Airflow'.

## Note
During the work for this chapter, a bug in Airflow forced a downgrade of the Postgres provider. The bug is described [here](https://github.com/apache/airflow/issues/41373).
The workaround was to pin the Postgres provider to version 5.0.0:
```
apache-airflow-providers-postgres==5.0.0
```


## Contents

This code example contains the following DAGs:

- 01_dag_cycle.py
- 02_bash_operator_no_command.py
- 03_duplicate_task_ids.py
- 04_nodags.py
- 05_testme.py
- 06_dagtestdag.py

The first 4 are intended to fail and serve to show the DAG Integrity Tests.

The `custom` directory contains a custom Hook and a number of operators, that were introduced in chapter 8. We use these 
to show how to write tests for your (custom) operators. Tests can be found in the corresponding `tests` directory.

## Usage

To get started with the code examples, start Airflow in docker using the following command:

```
docker-compose up -d --build
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

```
docker-compose down -v
```
