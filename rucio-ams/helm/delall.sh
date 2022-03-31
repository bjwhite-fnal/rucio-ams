#!/bin/bash

# Use this to delete all of the resources associated with a Rucio deployment.

verify_project () {
    if [[ -z "$EXPERIMENT" ]]; then
        echo "Please provide a value for the EXPERIMENT environment variable"
        exit -1
    else
        # Important: ensures we have the okd project set to the experiment that we intend,
        #   so that we don't accidentally do dumb stuff to the wrong experiment's rucio deployment
        if ! [[ ${EXPERIMENT} == "rubin" ]]; then
            ocproject=$(oc project)
            proj=($ocproject)
            if ! [[ ${proj[2]} == "\"rucio-${EXPERIMENT}\"" ]]; then
                echo -e "\tPlease ensure that the Openshift project is set to rucio-${EXPERIMENT}"
                exit -3
            fi
        else
            kubecontext=$(kubectl config current-context)
            echo ${kubecontext}
            if ! [[ ${kubecontext} =~ *rubin* ]]; then
                echo -e "\tPlease ensure that the Kubernetes context is set to rucio-${EXPERIMENT}"
                exit -4
            fi
        fi
    fi
}

echo "**************** Removing Openshift application: rucio-$EXPERIMENT ****************"
verify_project
kubectl delete deployments --all
kubectl delete secrets --all
kubectl delete route --all
kubectl delete ingress --all
kubectl delete services --all
kubectl delete configmaps --all
kubectl delete cronjobs --all
kubectl delete pods --all --now
kubectl delete daemonset --all
kubectl delete pvc --all
kubectl delete jobs --all
kubectl delete serviceaccount rucio-int-rucio-edit
echo "**************** Openshift application rucio-$EXPERIMENT removed successfully. ****************" 
