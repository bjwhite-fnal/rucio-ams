FROM rabbitmq:3

RUN rabbitmq-plugins enable --offline rabbitmq_stomp
COPY docker-entrypoint.sh /usr/local/bin/

VOLUME /etc/rabbitmq/ssl
EXPOSE 61613 61614

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["rabbitmq-server"]
