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
- dagtestdag.py (Not numbered as this causes issues when importing the module in pytest...)

These DAGs are not intended to run in the UI (some even fail deliberately) and are there to show how to use tests. Because they are not intended, they have been explicitly added to the 
`.airflowignore` file to avoid errors showing up in the UI.

The `dags/custom` directory contains a custom Hook and a number of operators, that were introduced in chapter 8. We use these 
to show how to write tests for your (custom) operators. Tests can be found in the corresponding `tests` directory.

## Usage

To get started with the code examples, start Airflow in docker using the following command:

```
docker-compose up
```

Wait for a few seconds and you should be able to access the examples at http://localhost:8080/.

To stop running the examples, run the following command:

```
docker-compose down -v
```

For running the tests themselves, we recommend using a local Python environment. This is because some of the tests depend on Docker to run services in, e.g. Postgres.
To avoid issues with Docker-in-Docker, using a virtual environment is the best way to go. To set this up:

```bash
python -m venv my-venv
source my-venv/bin/activate
pip install -r requirements.txt
airflow db init
```
The last line is needed to initialize a local Airflow database (which is needed for some of the tests). By default this will be a sqlite database in the default `AIRFLOW_HOME` path. If you want something else, the configuration is left to you.

You should now be able to run the tests, e.g.
```bash
pytest tests/
```
Please note that Docker is a requirement for running all tests. The tests  that use Docker (test_dagtestdag and test_movielens_to_postgres_operator) can exhibit flaky behaviour, so they have been marked with `@flaky`. This setup was confirmed to work with Python 3.12.4