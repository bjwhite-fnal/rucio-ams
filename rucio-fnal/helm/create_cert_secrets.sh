#!/bin/bash

kubectl create secret generic host-cert \
	--from-file=hostcert.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-cert.pem
kubectl create secret generic host-key \
	--from-file=hostkey.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-key.pem
kubectl create secret generic ca-bundle \
	--from-file=ca.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/ca_bundle.pem 

# the 3 above, combined
kubectl create secret generic ssl-secrets \
	--from-file=hostcert.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-cert.pem \
	--from-file=hostkey.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-key.pem \
	--from-file=ca.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/ca_bundle.pem 

# Use host cert for FTS access for conveyor
kubectl create secret generic fts-secrets \
	--from-file=fts_usercert.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-cert.pem \
	--from-file=fts_userkey.pem=$FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs/rucio-dev.fnal.gov-key.pem 
