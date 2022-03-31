#!/bin/sh

# TODO: Switch to using Kubernetes Ingresses instead of OKD routes
oc create -f $RUCIO_AMS_DIR/$EXPERIMENT/routes.yaml
