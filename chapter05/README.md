# Chapter 5

Code accompanying Chapter 5 of the book 'Data pipelines with Apache Airflow'.

## Contents

This code example contains the following DAGs:

- 01_rocket_pipeline_dependencies.py - Initial DAG with several tasks.
- 02_branch_function.py - Branching within a function.
- 03_branch_dag_old_new.py - Branching within the DAG.
- 04_branch_dag_join.py - Branching within the DAG with a join.
- 05_condition_function.py - Condition within a function.
- 06_condition_dag.py - Condition within the DAG.
- 07_latest_only_condition.py - Condition for latest only.
- 08_trigger_rules.py - DAG illustrating several trigger rules.
- 09_xcoms.py - Xcoms basics.
- 10_xcoms_template.py - Xcoms with templating.
- 11_xcoms_return.py - Default XComs.
- 12_taskflow.py - Taskflow API.
- 13_dag_decorator.py - Using a dag decorator.
- 14_taskflow_mixed_operators.py - Mixon taskflow and 'normal' tasks.

## Usage

To get started with the code examples, start Airflow in docker using the following command:

```bash
docker compose up -d
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

```bash
docker compose down -v
```
