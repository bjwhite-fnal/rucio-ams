#!/bin/bash

####
# Run this in order to create secrets for use by the Openshift deployment. Secret names are referred to by the Helm templates.
####

# Server
kubectl create secret generic rucio-$EXPERIMENT-server-hostcert \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-server-hostkey \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-server-cafile \
        --from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE

# Auth Server

kubectl create secret generic rucio-$EXPERIMENT-auth-hostcert \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-auth-hostkey \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-auth-cafile \
        --from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE


# Daemons
kubectl create secret generic rucio-$EXPERIMENT-rucio-x509up \
        --from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT \
        --from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY \

kubectl create secret generic rucio-$EXPERIMENT-fts-cert \
        --from-file=usercert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-fts-key \
        --from-file=new_userkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-rucio-ca-bundle \
        --from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE

# Reapers need the whole directory of certificates
mkdir /tmp/reaper-certs
cp /etc/grid-security/certificates/*.0 /tmp/reaper-certs/
cp /etc/grid-security/certificates/*.signing_policy /tmp/reaper-certs/
kubectl create secret generic rucio-$EXPERIMENT-rucio-ca-bundle-reaper \
        --from-file=/tmp/reaper-certs
rm -r /tmp/reaper-certs

# Hermes
kubectl create secret generic rucio-$EXPERIMENT-hermes-cert \
        --from-file=usercert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-hermes-key \
        --from-file=new_userkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY

# WebUI
kubectl create secret generic rucio-$EXPERIMENT-hostcert \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-hostkey \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-cafile \
        --from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE

# Messenger
kubectl create secret generic ssl-secrets \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY \
	--from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE 

# ESCron
kubectl create secret generic rucio-$EXPERIMENT-escron-hostcert \
        --from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-escron-hostkey \
        --from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY
