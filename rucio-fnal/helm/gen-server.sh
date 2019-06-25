#!/bin/sh

# Use two files for specifying values so as to keep secrets separate
if [ -z "$FNAL_EXP_RUCIO_CONF_DIR" ]; then
    echo "Please use FNAL_EXP_RUCIO_CONF_DIR to specify a source directory for configuration options."
    exit 1
elif [ -z "$EXPERIMENT" ]; then
    echo "Please use EXPERIMENT to specify the name of the experiment you wish to generate config files for."
    exit 1
else
    helm template --name rucio-$EXPERIMENT $RUCIO_HELM_TEMPLATE_DIR/server -f $FNAL_EXP_RUCIO_CONF_DIR/helm/server/values.yaml -f $FNAL_EXP_RUCIO_CONF_DIR/helm/secret/config.yaml > $FNAL_EXP_RUCIO_CONF_DIR/server.yaml
fi
