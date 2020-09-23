# Dockerfile for the FNAL Rucio Logstash image

FROM docker.elastic.co/logstash/logstash:7.8.1

#RUN rm -f /usr/share/logstash/pipeline/logstash.conf
#ADD pipeline/ /usr/share/logstash/pipeline/
#ADD config/ /usr/share/logstash/config/


RUN rm -f /usr/share/logstash/pipeline/logstash.conf
ADD ./logstash.conf /usr/share/logstash/pipeline/logstash.conf
RUN rm -f /usr/share/logstash/config/logstash.yml
ADD ./logstash.yml /usr/share/logstash/config/logstash.yml

VOLUME /var/logs/rucio

USER root
RUN yum install -y gettext net-tools
RUN chown logstash:logstash /usr/share/logstash/pipeline/logstash.conf
USER logstash

ADD ./docker-entrypoint.sh /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
