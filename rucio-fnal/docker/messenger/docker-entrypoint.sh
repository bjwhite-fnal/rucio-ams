#!/bin/bash

set -x

# allow the container to be started with `--user`
if [[ "$1" == rabbitmq* ]] && [ "$(id -u)" = '0' ]; then
	if [ "$1" = 'rabbitmq-server' ]; then
		chown -R rabbitmq /var/lib/rabbitmq
	fi
	exec gosu rabbitmq "$BASH_SOURCE" "$@"
fi

# Populate the RabbitMQ configuration file with the service values to listen on
envsubst < configure-rabbitmq.sh > configure-rabbitmq.sh
configure-rabbitmq.sh

exec "$@"
