# Dockerfile for configration of image to be used as a Prometheus Server to scrape container metrics

FROM prom/prometheus:latest

USER root
COPY ./docker-entrypoint.sh /prometheus/docker-entrypoint.sh
RUN chown nobody:nobody /prometheus/docker-entrypoint.sh

COPY ./prometheus.yml /etc/prometheus/
RUN chown nobody:nobody /etc/prometheus/prometheus.yml
USER nobody

ENTRYPOINT [ "/prometheus/docker-entrypoint.sh" ]
#ENTRYPOINT [ "ls", "-l", "/prometheus", "/etc/prometheus" ]
#ENTRYPOINT [ "id" ]
#ENTRYPOINT [ "sleep", "100000" ]
