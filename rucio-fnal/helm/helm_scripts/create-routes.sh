#!/bin/sh

# TODO: Switch to using Kubernetes Ingresses instead of OKD routes
oc create -f $FNAL_RUCIO_DIR/$EXPERIMENT/routes.yaml
