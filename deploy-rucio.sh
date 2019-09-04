#!/bin/bash

# Use this to deploy Rucio for an experiment. Create and use an Openshift project named rucio-<experiment name>. Make sure you have the proper configurations setup and
#   the environment is correct with FNAL_RUCIO_DIR set.

verify_project () {
    # Verify that the currently active Openshift project appears to be correct for the value in EXPERIMENT and all other required environment variables are set
    if [[ -z $EXPERIMENT ]]; then
        echo "Please provide a value for the EXPERIMENT environment variable"
        exit -1
    elif [[ -z $FNAL_RUCIO_DIR ]]; then
        echo "Please provide a value for the FNAL_RUCIO_DIR environment variable"
        exit -1
    elif [[ -z $FNAL_EXP_RUCIO_CERT ]]; then
        echo "Please provide a value for the FNAL_EXP_RUCIO_CERT environment variable"
        exit -1
    elif [[ -z $FNAL_EXP_RUCIO_KEY ]]; then
        echo "Please provide a value for the FNAL_EXP_RUCIO_KEY environment variable"
        exit -1
    elif [[ -z $FNAL_EXP_RUCIO_CA_BUNDLE ]]; then
        echo "Please provide a value for the FNAL_EXP_RUCIO_CA_BUNDLE environment variable"
        exit -1
    else
        ocproject=$(oc project)
        proj=($ocproject)
        if ! [[ ${proj[2]} == "\"rucio-$EXPERIMENT\"" ]]; then 
            echo "Please ensure that the Openshift project is set to rucio-$EXPERIMENT"
            exit -3
        fi
    fi
}

echo "**************** Initializing Openshift Application: rucio-$EXPERIMENT ****************"
verify_project
echo "Creating application secrets..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create_cert_secrets.sh
echo "Generating configuration files..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/gen-daemons.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/gen-server.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/gen-osg-authentication.sh
echo "Creating cache service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create-cache.sh
echo "Creating messenger service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create-messenger.sh
echo "Creating servers..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create-server.sh
echo "Creating daemons..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create-daemons.sh
echo "Creating OSG authentication service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/create-osg-authentication.sh
echo "**************** Openshift application rucio-$EXPERIMENT deployment successful ****************" 
