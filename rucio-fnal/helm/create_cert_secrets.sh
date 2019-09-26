#!/bin/bash

# Run this in order to create secrets for use by the Openshift application.

kubectl create secret generic host-cert \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT
kubectl create secret generic host-key \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY
kubectl create secret generic ca-bundle \
	--from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE 

# the 3 above, combined
kubectl create secret generic ssl-secrets \
	--from-file=hostcert.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CERT \
	--from-file=hostkey.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_KEY \
	--from-file=ca.pem=$FNAL_RUCIO_DIR/$EXPERIMENT/certs/$FNAL_EXP_RUCIO_CA_BUNDLE 
