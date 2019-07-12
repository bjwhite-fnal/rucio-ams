#!/bin/sh -f

if [ -z "${NO_CACHE_DOCKER_BUILD}" ]; then
    docker build -t rucio-server server
else
    docker build --no-cache -t rucio-server server
fi
