#!/bin/bash

# Use this to delete all of the resources associated with a Rucio deployment.

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

echo "**************** Removing Openshift application: rucio-$EXPERIMENT ****************"
verify_project
oc delete deployments --all
oc delete secrets --all
oc delete route --all
oc delete services -l "app=rucio-server"
oc delete services -l "app=rucio-server-auth"
oc delete services -l "app=rucio-cache-cache"
oc delete configmaps --all
oc delete ingress --all
oc delete cronjobs --all
oc delete pods --all --now
echo "**************** Openshift application rucio-$EXPERIMENT removed successfully. ****************" 
