# Dockerfile for the FNAL Rucio logging Filebeat image

FROM docker.elastic.co/beats/filebeat:7.8.0

RUN rm /filebeat.yml
ADD ./filebeat.yml /etc/filebeat/filebeat.yml 
ADD ./docker-entrypoint.sh /docker-entrypoint.sh

VOLUME /var/logs/rucio

USER root
RUN chown root:filebeat /etc/filebeat/filebeat.yml
USER filebeat

ENTRYPOINT ["/docker-entrypoint.sh"]
