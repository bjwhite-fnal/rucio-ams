# Dockerfile for configration of image to be used as a Prometheus Server to scrape container metrics

FROM prom/prometheus:latest
USER root
ADD docker-entrypoint.sh /bin/docker-entrypoint.sh
ADD prometheus.yml.template /prometheus
#ADD prometheus.yml /etc/prometheus/
#ENTRYPOINT [ "/tmp/docker-entrypoint.sh" ]
USER nobody
ENTRYPOINT [ "/bin/docker-entrypoint.sh" ]
