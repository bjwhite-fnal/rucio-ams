#!/bin/sh -f

if [[ -z $NO_CACHE_DOCKER_BUILD ]]; then
    docker build -t rucio-messenger messenger
else
    docker build --no-cache -t rucio-messenger messenger
fi
