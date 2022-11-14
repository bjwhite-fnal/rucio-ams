#!/bin/bash

####
# Run this in order to create secrets for use by the Openshift deployment. Secret names are referred to by the Helm templates.
####

# Server
kubectl create secret generic rucio-$EXPERIMENT-server-hostcert \
	--from-file=hostcert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-server-hostkey \
	--from-file=hostkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-server-cafile \
        --from-file=ca.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CA_BUNDLE

# Auth Server

kubectl create secret generic rucio-$EXPERIMENT-auth-hostcert \
	--from-file=hostcert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-auth-hostkey \
	--from-file=hostkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-auth-cafile \
        --from-file=ca.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CA_BUNDLE


# Daemons
kubectl create secret generic rucio-$EXPERIMENT-rucio-x509up \
        --from-file=hostcert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT \
        --from-file=hostkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY \

kubectl create secret generic rucio-$EXPERIMENT-fts-cert \
        --from-file=usercert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-fts-key \
        --from-file=new_userkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-rucio-ca-bundle \
        --from-file=ca.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CA_BUNDLE

# Reapers need the whole directory of certificates
mkdir /tmp/reaper-certs
cp /etc/grid-security/certificates/*.0 /tmp/reaper-certs/
cp /etc/grid-security/certificates/*.signing_policy /tmp/reaper-certs/
kubectl create secret generic rucio-$EXPERIMENT-rucio-ca-bundle-reaper \
        --from-file=/tmp/reaper-certs
rm -r /tmp/reaper-certs

# Hermes
kubectl create secret generic rucio-$EXPERIMENT-hermes-cert \
        --from-file=usercert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-hermes-key \
        --from-file=new_userkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY

# WebUI
kubectl create secret generic rucio-$EXPERIMENT-hostcert \
	--from-file=hostcert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT

kubectl create secret generic rucio-$EXPERIMENT-hostkey \
	--from-file=hostkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY

kubectl create secret generic rucio-$EXPERIMENT-cafile \
        --from-file=ca.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CA_BUNDLE

# Messenger
kubectl create secret generic ssl-secrets \
	--from-file=hostcert.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CERT \
	--from-file=hostkey.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_KEY \
	--from-file=ca.pem=$RUCIO_AMS_DIR/$EXPERIMENT/certs/$AMS_RUCIO_CA_BUNDLE 

# Replica Recoverer
kubectl create secret generic rucio-$EXPERIMENT-suspicious-replica-recoverer-input \
	--from-file=suspicious_replica_recoverer.json=$RUCIO_AMS_DIR/$EXPERIMENT/suspicious_replica_recoverer.json

# Automatix
kubectl create secret generic rucio-$EXPERIMENT-automatix-input \
	--from-file=automatix.json=$RUCIO_AMS_DIR/$EXPERIMENT/automatix.json
