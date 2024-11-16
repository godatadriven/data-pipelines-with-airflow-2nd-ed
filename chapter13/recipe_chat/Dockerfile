FROM python:3.12-slim


ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=off
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV APP_DIR="/app"
ENV POETRY_VERSION=1.8.4
ENV LANG=C.UTF-8 LC_ALL=C.UTF-8
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1

WORKDIR $APP_DIR

RUN pip install "poetry==$POETRY_VERSION"

COPY pyproject.toml poetry.lock ./

RUN poetry install --no-root --no-dev  --no-ansi

COPY . .

RUN poetry install --only-root --no-ansi
EXPOSE 8084

CMD ["poetry", "run", "streamlit", "run", "src/recipe_chat/Recipe_tool.py",  "--server.port=8084", "--server.address=0.0.0.0"]


