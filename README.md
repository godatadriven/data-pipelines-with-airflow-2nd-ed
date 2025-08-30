# Data Pipelines with Apache Airflow

Code accompanying the Manning book [Data Pipelines with Apache Airflow](https://www.manning.com/books/data-pipelines-with-apache-airflow).

### Structure

Overall, this repository is structured as follows:

```
├── chapter01                # Code examples for Chapter 1.
├── chapter02                # Code examples for Chapter 2.
├── ...
├── .pre-commit-config.yaml  # Pre-commit config for the CI.
├── CHANGELOG.md             # Changelog detailing updates to the code.
├── LICENSE                  # Code license.
├── README.md                # This readme.
└── requirements.txt         # CI dependencies.
```

The *chapterXX* directories contain the code examples for each specific Chapter.

Code for each Chapter is generally structured something like follows:

```
├── dags                  # Airflow DAG examples (+ other code).
├── docker-compose.yml    # Docker-compose file used for running the Chapter's containers.
└── readme.md             # Readme with Chapter-specific details, if any.
```

### Usage

Details for running specific chapter examples are available in the corresponding chapter's readme. In general, most code examples are run using docker-compose, together with the provided docker-compose.yml file in each chapter. This docker-compose file will take care of spinning up the required resources and start an Airflow instance for you. Once everything is running, you should be able to run the examples in Airflow using your local browser.

Some later Chapters (such as Chapters 11 and 13) may require a bit more setup. The details for doing so are described in the corresponding readme's and in the Chapter's themselves.


### Validation in CI setting

To enable validating all dags of all chapters in a CI setting the script `validate-dag-runs.sh` is available.

#### Running the validation

```bash
./validate-dag-runs.sh -c chapter01
./validate-dag-runs.sh -c chapter02
./validate-dag-runs.sh -c chapter11/docker
```

#### TODO

- Add config file to enable validating dags that are expected to fail
- Add config file to be able to ignore dag directories (like chapter10/tests/dags)
- Add ways to check dag state for dags that have multiple runs (chapter11/docker has 3 runs for example. The current sript only checks if 1 of them succeeded.)

- Add script to update airflow version in envs, dockerfiles etc
```bash
sed -i -e 's/\"3\.0\.5rc2\"/\"3.0.6\"/g' chapter17/values/*.yaml
sed -i -e 's/apache\/airflow:3\.0\.5rc2/apache\/airflow:3.0.6/g' chapter*/.env
sed -i -e 's/apache\/airflow:3\.0\.5rc2/apache\/airflow:3.0.6/g' chapter*/Dockerfile.*
```
