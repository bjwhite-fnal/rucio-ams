#!/bin/sh

# Use two files for specifying values so as to keep secrets separate
if [ -z "$FNAL_RUCIO_DIR" ]; then
    echo "Please use FNAL_RUCIO_DIR to specify a top level directory for the deployment system."
    exit 1
elif [ -z "$EXPERIMENT" ]; then
    echo "Please use EXPERIMENT to specify the name of the experiment you wish to generate config files for."
    exit 1
else
    helm template --name rucio-$EXPERIMENT-filebeat $FNAL_RUCIO_DIR/rucio-fnal/helm/helm-fnal/filebeat \
        --set experiment=$EXPERIMENT \
        --set image.tag=$FNAL_RUCIO_VERSION \
        -f $FNAL_RUCIO_DIR/$EXPERIMENT/helm/filebeat/values.yaml > $FNAL_RUCIO_DIR/$EXPERIMENT/filebeat.yaml
fi
