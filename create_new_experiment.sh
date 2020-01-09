#!/bin/bash

# Use this script to quickly create the configuration structure for a new
# Rucio deployment on an Openshift Cluster
# Usage:
#   ./create_new_experiment.sh <experiment> <external IP address>

# $1 : experiment
if [ -z $1 ]; then
    echo "Please provide an experiment name as the first argument."
    exit 0
fi

# $2 : external IP address
if [ -z $2 ]; then
    echo "Please provide an external IP address for this Rucio deployment"
    exit 0
else
    if [[ ! "$2" =~ ^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$ ]]; then # Check valid IP address
        echo "Please provide a properly formatted external IP address (xxx.xxx.xxx.xxx)"
        exit 0
    fi
fi

experiment=${1,,}
external_ip=$2
db_conn_str=$3


# Create new exp directory structure
cp -r experiment_config_template/ $experiment

# Replace placeholders with provided values
sed -i "s/REPLACE_ME_EXPERIMENT/$experiment/g" $experiment/setup_rucio_env.sh
for f in `find $experiment/helm -name "*.yaml"`
do
    sed -i "s/REPLACE_ME_EXPERIMENT/$experiment/g" $f
    sed -i "s/REPLACE_ME_EXT_IP/$external_ip/g" $f
    # The following assumes that there are no semicolons in the database connection string that will conflict with the sed delimiters.
    sed -i "s;REPLACE_ME_DB_CONN_STR;$db_conn_str;g" $f
done
