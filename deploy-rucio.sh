#!/bin/bash

# Use this to deploy Rucio for an experiment. Create and use an Openshift project named rucio-<experiment name>. Make sure you have the proper configurations setup and
#   the environment is correct with FNAL_RUCIO_DIR set.


verify_environment () {
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
verify_environment

echo "Creating application secrets..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create_cert_secrets.sh

echo "Generating configuration files..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-daemons.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-server.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-cache.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-messenger.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-webui.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-routes.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-filebeat.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-logstash.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-logrotate.sh

echo "Creating cache service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-cache.sh > /dev/null

echo "Creating messenger service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-messenger.sh > /dev/null

echo "Creating Filebeat logging scraper..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-filebeat.sh > /dev/null

echo "Creating Logstash logging processor..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-logstash.sh > /dev/null

echo "Creating logrotate logging filesystem management..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-logrotate.sh > /dev/null

echo "Creating daemons..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-daemons.sh > /dev/null

echo "Creating servers..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-server.sh > /dev/null

echo "Creating web UI..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-webui.sh > /dev/null

echo "Creating networking routes..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-routes.sh > /dev/null

echo "**************** Openshift application rucio-$EXPERIMENT deployment successful ****************" 

echo "Setting the Reaper2 log level to ERROR only so that it does not take up the whole log volume."
oc set env deployment.apps/rucio-${EXPERIMENT}-reaper2 RUCIO_CFG_COMMON_LOGLEVEL=ERROR
