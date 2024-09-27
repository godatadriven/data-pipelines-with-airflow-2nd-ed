#!/bin/bash

# Note: this script is a bit of a "hack" to run Airflow in a single container.
# This is obviously not ideal, but convenient for demonstration purposes.
# In a production setting, run Airflow in separate containers, as explained in Chapter 10.

set -x

SCRIPT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd)

docker run \
-ti \
-p 8080:8080 \
-v ${SCRIPT_DIR}/../dags/05_download_rocket_launches.py:/opt/airflow/dags/05_download_rocket_launches.py \
--rm \
--name airflow \
--entrypoint=/bin/bash \
apache/airflow:2.10.2-python3.12 \
-c '( \
airflow db migrate && \
airflow users create --username airflow --password airflow --firstname Anonymous --lastname Airflow --role Admin --email airflow@example.org \
); \
airflow webserver & \
airflow scheduler \
'
