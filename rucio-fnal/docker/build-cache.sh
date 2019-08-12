#!/bin/sh -f

if [[ -z $NO_CACHE_DOCKER_BUILD ]]; then
    docker build -t rucio-cache cache 
else
    docker build --no-cache -t  rucio-cache cache
fi
