#!/bin/bash

python3 /from_mq_to_es.py \
    ${RUCIO_BROKER_HOST} \
    ${RUCIO_BROKER_PORT} \
    ${RUCIO_BROKER_QUEUE} \
    ${RUCIO_BROKER_SUBSCRIPTION_ID} \
    ${CONSUMER_HOST} \
    ${CONSUMER_PORT}
