#!/bin/bash
id=$(id -u)

docker run \
    -v ${PWD}/grid-certs:/etc/grid-security/certificates \
    --env X509_USER_PROXY=/opt/rucio/etc/proxy \
    --name autotransfer \
    rucio-autotransfer
