FROM nginx:1.27-alpine

# Fixed variable used to offset dates returned by the taxi fileserver to the current year,
# so that the demo works in any year you run it in
ARG DATA_YEAR=2023
ENV DATA_YEAR=${DATA_YEAR}

RUN apk update && \
    apk add postgresql-client && \
    mkdir -p /data

COPY get_last_hour.sh /etc/periodic/15min/get_last_hour
COPY get_last_hour_reboot.sh /usr/local/bin/get_last_hour_reboot
COPY nginx.conf /etc/nginx/nginx.conf
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /etc/periodic/15min/get_last_hour && \
    chmod +x /usr/local/bin/get_last_hour_reboot && \
    chmod +x /entrypoint.sh && \
    echo "@reboot /usr/local/bin/get_last_hour_reboot" >> /etc/crontabs/root

ENTRYPOINT ["/entrypoint.sh"]
