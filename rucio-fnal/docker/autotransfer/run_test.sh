#!/bin/bash
echo -e "Running command: python3 /run_transfer_test.py \n\
    --experiment ${EXPERIMENT} \n\
    --host ${BROKER_HOST} \n\
    --port ${BROKER_PORT} \n\
    --cert ${BROKER_CERT} \n\
    --key ${BROKER_KEY} \n\
    --topic ${TOPIC} \n\
    --durable ${DURABLE} \n\
    --unsubscribe ${UNSUBSCRIBE} \n\
    --start_rse ${START_RSE} \n\
    --end_rses ${END_RSES} \n\
    --rucio_account ${RUCIO_ACCOUNT} \n\
    --num_files ${NUM_FILES} \n\
    --file_size ${FILE_SIZE}"

# We have to copy the certificates because we cannot change permissions on them as mounted secrets and
# voms-proxy is particular about permissions
echo -e "Generating proxy..."
cp /opt/certs/hostcert.pem /tmp/cert.pem
cp /opt/certs/hostkey.pem /tmp/key.pem
chmod 400 /tmp/key.pem

# Generate a proxy with the voms extension if requested
voms-proxy-init --debug \
    -rfc \
    -valid 96:00 \
    -cert /tmp/cert.pem \
    -key /tmp/key.pem \
    -out /tmp/x509up \
    -voms ${RUCIO_AUTOTRANSFER_VOMS} \
    -timeout 5

mkdir /opt/proxy
cp /tmp/x509up /opt/proxy/x509up

python3 /run_transfer_test.py \
    --experiment ${EXPERIMENT} \
    --host ${BROKER_HOST} \
    --port ${BROKER_PORT} \
    --cert ${BROKER_CERT} \
    --key ${BROKER_KEY} \
    --topic ${TOPIC} \
    --durable ${DURABLE} \
    --unsubscribe ${UNSUBSCRIBE} \
    --start_rse ${START_RSE} \
    --end_rses ${END_RSES} \
    --rucio_account ${RUCIO_ACCOUNT} \
    --num_files ${NUM_FILES} \
    --file_size ${FILE_SIZE}
    #--proxy ${X509_USER_PROXY}
