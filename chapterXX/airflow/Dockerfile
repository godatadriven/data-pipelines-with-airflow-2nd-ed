
FROM apache/airflow:2.8.1

USER airflow

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV APP_DIR="/app"

WORKDIR $APP_DIR

COPY ./requirements.txt ./

# Install dependencies
RUN pip install -r requirements.txt --no-cache-dir

COPY --chown=airflow:airflow . .


