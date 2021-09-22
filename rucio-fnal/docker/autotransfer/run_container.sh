#!/bin/bash
id=$(id -u)

docker run \
    -v ${PWD}/x509up_u${id}:/tmp/proxy \
    -v ${PWD}/grid-certs:/etc/grid-security/certificates \
    --name autotransfer \
    --env X509_USER_PROXY=/tmp/proxy \
    rucio-autotransfer
