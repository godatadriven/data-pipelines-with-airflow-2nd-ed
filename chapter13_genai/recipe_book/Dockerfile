FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV APP_DIR="/app"
ENV POETRY_VERSION=1.8.3
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

WORKDIR $APP_DIR

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false 
RUN poetry install --no-root --no-dev  

COPY . .

# Install the package
RUN poetry install --only-root

# ENTRYPOINT [ "recipe_book" ]