#!/bin/sh

# Use two files for specifying values so as to keep secrets separate
if [ -z "$FNAL_RUCIO_DIR" ]; then
    echo "Please use FNAL_RUCIO_DIR to specify a top level directory for the deployment system."
    exit 1
elif [ -z "$EXPERIMENT" ]; then
    echo "Please use EXPERIMENT to specify the name of the experiment you wish to generate config files for."
    exit 1
else
    helm template --name rucio-$EXPERIMENT $FNAL_RUCIO_DIR/rucio-fnal/helm/helm-charts/rucio-ui --set experiment=$EXPERIMENT -f $FNAL_RUCIO_DIR/$EXPERIMENT/helm/webui/values.yaml -f $FNAL_RUCIO_DIR/$EXPERIMENT/helm/secret/config.yaml > $FNAL_RUCIO_DIR/$EXPERIMENT/webui.yaml
fi
