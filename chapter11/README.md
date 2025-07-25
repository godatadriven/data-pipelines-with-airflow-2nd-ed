# Chapter 11

Code accompanying Chapter 11 of the book 'Data pipelines with Apache Airflow'.

## Contents

This code example contains the following three DAGs:

- 01_task_factory.py - Illustrates how to use a factory method for creating common patterns of tasks.
- 02_dag_factory.py - Demonstrates how to use a factory method to create multiple instances of similar DAGs.
- 03_task_groups.py - Shows how to use task groups
- 04_task_groups_umbrella.py - A more complex example for TaskGroups with the weather API example
- 05_sla_misses.py - Shows how to use Airflow SLA functionality in your DAGs to catch issues with long running tasks.
- 06_dynamic_task_mapping.py - Demonstration of traditional API setup with dynamic task mapping
- 07_dynamic_task_mapping_taskflow.py - Same as 06_dynamic_task_mapping.py but using the TaskFlow API.
- 08_dynamic_task_mapping_taskgroup.py - Demonstration of combination of dynamic task mapping with taskgroups
- 09_no_dynamic_task_mapping.py - Demonstration of the DAG if we didn't use dynamic task mapping

For Dynamic Task Mapping, we also include a super simple REST API that generates a random number (between 1 and 10) of movie reviews. With this, we can demonstrate how 
Dynamic Task Mapping allows you to dynamically structure your DAG based on the data structure/contents. This API is included in the Docker Compose environment.

## Usage

To get started with the code examples, start Airflow in docker using the following command:

```
docker compose up -d
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

```
docker compose down -v
```
