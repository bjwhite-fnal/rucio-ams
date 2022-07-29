#!/bin/bash

set -x

# Populate the RabbitMQ configuration file with the service values to listen on
envsubst < /usr/local/bin/configure-rabbitmq.sh > /usr/local/bin/configure-rabbitmq.sh.tmp
mv /usr/local/bin/configure-rabbitmq.sh.tmp /usr/local/bin/configure-rabbitmq.sh
chmod +x /usr/local/bin/configure-rabbitmq.sh
/usr/local/bin/configure-rabbitmq.sh

exec "$@"
