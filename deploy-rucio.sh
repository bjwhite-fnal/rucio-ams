#!/bin/bash

# Use this to deploy Rucio for an experiment. Create and use an Openshift project named rucio-< experiment name >. Make sure you have the proper configurations setup and
#   the environment is correct with FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR and RUCIO_HELM_TEMPLATE_DIR set.
export RUCIO_HELM_TEMPLATE_DIR=$PWD/rucio-fnal/helm

verify_project () {
    if [[ -z "$EXPERIMENT" ]]; then
        echo "Please provide a value for the EXPERIMENT environment variable"
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
./rucio-fnal/helm/create_cert_secrets.sh
echo "Generating configuration files..."
./rucio-fnal/helm/gen-daemons.sh
./rucio-fnal/helm/gen-server.sh
echo "Creating servers..."
./rucio-fnal/helm/create-server.sh
echo "Creating daemons..."
./rucio-fnal/helm/create-daemons.sh
echo "**************** Openshift application rucio-$EXPERIMENT deployment successful ****************" 
