#!/bin/bash
id=$(id -u)

docker run \
    -v ${PWD}/grid-certs:/etc/grid-security/certificates \
    -v /tmp/x509up_u${id}:/opt/rucio/etc/proxy \
    -v ${PWD}/ca_bundle.pem:/opt/certs/ca.pem \
    --env X509_USER_PROXY=/opt/rucio/etc/proxy \
    --env EXPERIMENT=int \
    --env BROKER_HOST=msg-int-rucio.okd.fnal.gov \
    --env BROKER_PORT=443 \
    --env BROKER_CERT=/opt/rucio/etc/proxy \
    --env BROKER_KEY=/opt/rucio/etc/proxy \
    --env TOPIC=/topic/rucio.events.int \
    --env DURABLE=False \
    --env UNSUBSCRIBE=False \
    --env START_RSE=DCACHE_BJWHITE_START \
    --env END_RSES=DCACHE_BJWHITE_END,DCACHE_BJWHITE_END2 \
    --env RUCIO_ACCOUNT=root \
    --env NUM_FILES=1 \
    --env FILE_SIZE=1024 \
    --name autotransfer \
    rucio-autotransfer
