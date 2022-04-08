#!/bin/sh

# Use two files for specifying values so as to keep secrets separate
if [ -z "$RUCIO_AMS_DIR" ]; then
    echo "Please use RUCIO_AMS_DIR to specify a top level directory for the deployment system."
    exit 1
elif [ -z "$EXPERIMENT" ]; then
    echo "Please use EXPERIMENT to specify the name of the experiment you wish to generate config files for."
    exit 1
else
    helm template --release-name rucio-$EXPERIMENT-exporter $RUCIO_AMS_DIR/rucio-ams/helm/helm-fnal/exporter \
        --set image.tag=$RUCIO_AMS_VERSION_TAG \
        -f $RUCIO_AMS_DIR/$EXPERIMENT/helm/exporter/values.yaml > $RUCIO_AMS_DIR/$EXPERIMENT/exporter.yaml
fi
