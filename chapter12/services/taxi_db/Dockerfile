FROM python:3.12 AS transformer

ARG DATA_YEAR=2023
ENV DATA_YEAR=${DATA_YEAR}

COPY data-init.sh /data-init.sh
COPY convert_pq_to_csv.py /convert_pq_to_csv.py
RUN pip install pyarrow
RUN mkdir -p /data && /data-init.sh

FROM postgres:16-alpine AS builder

ARG DATA_YEAR=2023
ENV DATA_YEAR=${DATA_YEAR}
ENV POSTGRES_HOST_AUTH_METHOD=trust
COPY postgres-init.sh /docker-entrypoint-initdb.d/postgres-init.sh
COPY --from=transformer /data /csvdata

RUN apk update && \
    apk add ca-certificates && \
    update-ca-certificates && \
    mkdir -p /data && \
    /usr/local/bin/docker-entrypoint.sh postgres && \
    cp -R /var/lib/postgresql/data/* /data

FROM postgres:16-alpine
ARG DATA_YEAR=2023
ENV DATA_YEAR=${DATA_YEAR}

COPY --from=builder /data /var/lib/postgresql/data
