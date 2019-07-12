#!/bin/sh -f

if [ -z "${NO_CACHE_DOCKER_BUILD}" ]; then
    docker build -t rucio-daemons-base daemons-base
else
    docker build --no-cache -t rucio-daemons-base daemons-base
fi
