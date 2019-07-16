#!/bin/sh -f

if [[ -z $NO_CACHE_DOCKER_BUILD ]]; then
    docker build -t rucio-daemons daemons
else
    docker build --no-cache -t rucio-daemons daemons
fi
