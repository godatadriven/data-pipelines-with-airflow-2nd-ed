FROM python:3.12-slim AS builder

RUN pip install poetry==1.8.4

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN --mount=type=cache,target=$POETRY_CACHE_DIR poetry install --without dev --no-root

COPY src ./src
COPY sample_recipes ./sample_recipes

RUN poetry install --only-root

FROM python:3.12-slim AS runtime

ENV VIRTUAL_ENV=/app/.venv \
    APP_SRC=/app/src \
    APP_DATA=/app/sample_recipes \
    PATH="/app/.venv/bin:$PATH"

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY --from=builder ${APP_SRC} ${APP_SRC}
COPY --from=builder ${APP_DATA} ${APP_DATA}

ENTRYPOINT ["recipe_book"]

