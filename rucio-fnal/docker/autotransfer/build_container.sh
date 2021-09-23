#!/bin/bash
export DOCKER_BUILDKIT=1

docker build --no-cache \
    -t rucio-autotransfer \
    ${PWD}
