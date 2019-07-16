#!/bin/sh -f

if [[ -z $NO_CACHE_DOCKER_BUILD ]]; then
    docker build -t rucio-server-base server-base
else
    docker build --no-cache -t rucio-server-base server-base
fi
