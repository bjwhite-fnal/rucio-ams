#!/bin/bash
echo "Running command: python3 /run_transfer_test.py \
    --experiment ${EXPERIMENT} \
    --host ${BROKER_HOST} \
    --port ${BROKER_PORT} \
    --topic ${TOPIC} \
    --durable ${DURABLE} \
    --unsubscribe ${UNSUBSCRIBE} \
    --start_rse ${START_RSE} \
    --end_rses ${END_RSES} \
    --rucio_account ${RUCIO_ACCOUNT} \
    --num_files ${NUM_FILES} \
    --file_size ${FILE_SIZE}"
sleep 1000000
python3 /run_transfer_test.py \
    --experiment ${EXPERIMENT} \
    --host ${BROKER_HOST} \
    --port ${BROKER_PORT} \
    --topic ${TOPIC} \
    --durable ${DURABLE} \
    --unsubscribe ${UNSUBSCRIBE} \
    --start_rse ${START_RSE} \
    --end_rses ${END_RSES} \
    --rucio_account ${RUCIO_ACCOUNT} \
    --num_files ${NUM_FILES} \
    --file_size ${FILE_SIZE}
    # Using defaults for the following
    #--cert ${BROKER_CERT} \
    #--key ${BROKER_KEY} \
    #--proxy ${X509_USER_PROXY}
