FROM postgres:16-alpine AS builder

ENV POSTGRES_HOST_AUTH_METHOD=trust
COPY postgres-init.sh /docker-entrypoint-initdb.d/postgres-init.sh
RUN apk update && \
    apk add ca-certificates && \
    update-ca-certificates && \
    mkdir -p /data && \
    /usr/local/bin/docker-entrypoint.sh postgres && \
    cp -R /var/lib/postgresql/data/* /data

FROM postgres:16-alpine
COPY --from=builder /data /var/lib/postgresql/data
