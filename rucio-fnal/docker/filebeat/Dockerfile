# Dockerfile for the FNAL Rucio logging Filebeat image

FROM docker.elastic.co/beats/filebeat:7.8.0

ADD ./filebeat.yml /usr/share/filebeat/filebeat.yml 
ADD ./docker-entrypoint.sh /docker-entrypoint.sh

VOLUME /var/logs/rucio

USER root
RUN yum install -y gettext net-tools openssl

RUN chown filebeat:filebeat /usr/share/filebeat/filebeat.yml
USER filebeat

ENTRYPOINT ["/docker-entrypoint.sh"]
