FROM rabbitmq:3

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get -y install gettext-base
RUN apt-get install -y net-tools lsof
RUN rabbitmq-plugins enable --offline rabbitmq_stomp

COPY ./configure-rabbitmq.sh /usr/local/bin/
COPY ./docker-entrypoint.sh /usr/local/bin/

VOLUME /etc/rabbitmq/ssl
EXPOSE 61613 61614

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["rabbitmq-server"]
