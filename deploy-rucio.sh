#!/bin/bash

# Use this to deploy Rucio for an experiment. Make sure you have the proper configurations setup and
#   the environment is correct with FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR and RUCIO_HELM_TEMPLATE_DIR set.
export RUCIO_HELM_TEMPLATE_DIR=$PWD/rucio-fnal/helm

echo "Creating application secrets..."
./rucio-fnal/helm/create_cert_secrets.sh
echo "Generating configuration files..."
./rucio-fnal/helm/gen-daemons.sh
./rucio-fnal/helm/gen-server.sh
echo "Creating servers..."
./rucio-fnal/helm/create-server.sh
echo "Creating daemons..."
./rucio-fnal/helm/create-daemons.sh
