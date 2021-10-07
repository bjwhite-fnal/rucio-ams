#!/bin/bash

# Use this to deploy Rucio for an experiment.
# Create and use an Openshift project named rucio-<experiment name>.
# Make sure you have the proper configurations setup and
#   the environment is correct with FNAL_RUCIO_DIR set.

verify_environment () {
    # Verify that the currently active Openshift project appears to be correct for the value 
    #    in EXPERIMENT and all other required environment variables are set
    echo -e "\tVerifying that the environment is configured correctly for Rucio deployment."
    # REQUIRED TO BE PRESENT
    for fnal_cfg_env in \
        EXPERIMENT \
        FNAL_RUCIO_DIR \
        FNAL_EXP_RUCIO_CERT \
        FNAL_EXP_RUCIO_KEY \
        FNAL_EXP_RUCIO_CA_BUNDLE
    do
        if [[ -z $fnal_cfg_env ]]; then
            echo -e "\tPlease provide a value for the ${fnal_cfg_env} environment variable"
            exit -1
        fi
    done

    # If you assign an ExternalIP to any service, verify we do it to them all
    if [[ -n ${FNAL_RUCIO_EXT_SERVER_IP} || \
            -n ${FNAL_RUCIO_EXT_AUTH_IP} || \
            -n ${FNAL_RUCIO_EXT_MSG_IP} || \
            -n ${FNAL_RUCIO_EXT_WEBUI_IP} ]]; then
        if [[ -z ${FNAL_RUCIO_EXT_SERVER_IP} || \
                -z ${FNAL_RUCIO_EXT_AUTH_IP} || \
                -z ${FNAL_RUCIO_EXT_MSG_IP} || \
                -z ${FNAL_RUCIO_EXT_WEBUI_IP} ]]; then
            echo -e "\tPlease ensure that all [FNAL_RUCIO_EXT_SERVER_IP, FNAL_RUCIO_EXT_AUTH_IP, FNAL_RUCIO_EXT_MSG_IP, FNAL_RUCIO_EXT_WEBUI_IP] are set if any of them are set."
            exit -2
        fi
    fi
    # IMPORTANT: Ensures we have the OKD project set to the experiment that we intend,
    #   so that we don't accidentally do dumb stuff to the wrong experiment's Rucio deployment
    ocproject=$(oc project)
    proj=($ocproject)
    if ! [[ ${proj[2]} == "\"rucio-$EXPERIMENT\"" ]]; then 
        echo -e "\tPlease ensure that the Openshift project is set to rucio-$EXPERIMENT"
        exit -3
    fi
}

echo -e "**************** Initializing Openshift Application: rucio-$EXPERIMENT ****************"
verify_environment

echo -e "\tCreating application secrets..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create_cert_secrets.sh

echo -e "\tCreating StatsD service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-statsd.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-statsd.sh > /dev/null

echo -e "\tCreating cache service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-cache.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-cache.sh > /dev/null

echo -e "\tCreating messenger service..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-messenger.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-messenger.sh > /dev/null

echo -e "\tCreating daemons..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-daemons.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-daemons.sh > /dev/null

echo -e "\tCreating servers..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-server.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-server.sh > /dev/null

echo -e "\tCreating web UI..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-webui.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-webui.sh > /dev/null

echo -e "\tCreating networking routes..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-routes.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-routes.sh > /dev/null

echo -e "\tCreating ElasticExporter..."
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/gen-escron.sh
$FNAL_RUCIO_DIR/rucio-fnal/helm/helm_scripts/create-escron.sh > /dev/null

echo -e "\tStarting the proxy generation cronjob."
kubectl create job --from=cronjob/rucio-${EXPERIMENT}-renew-fts-proxy ${USER}-manual-proxy-1

# Only bother with this if operating the OKD Services with OKD externalIPs
# Check if we have any
if [[ -n ${FNAL_RUCIO_EXT_SERVER_IP} || \
    -n ${FNAL_RUCIO_EXT_AUTH_IP} || \
    -n ${FNAL_RUCIO_EXT_WEBUI_IP} || \
    -n ${FNAL_RUCIO_EXT_MSG_IP} ]]; then
    # Ensure that we have all
    if [[ -z ${FNAL_RUCIO_EXT_SERVER_IP} || \
        -z ${FNAL_RUCIO_EXT_AUTH_IP} || \
        -z ${FNAL_RUCIO_EXT_WEBUI_IP} || \
        -z ${FNAL_RUCIO_EXT_MSG_IP} ]]; then
        echo -e "\tMake sure to set all ofFNAL_RUCIO_EXT_SERVER_IP, FNAL_RUCIO_EXT_AUTH_IP, FNAL_RUCIO_EXT_WEBUI_IP, FNAL_RUCIO_EXT_MSG_IP if you set any of them."
        exit -3
    else
        echo -e "\tApplying external IP addresses to the services."
        # Watch out for some tricky string concatenation to get the external ips into the spec string
        auth_server_service=$(oc get services | grep "server-auth" | awk '{print $1}')
        server_service=$(oc get services | grep "server" | grep -v "auth" | awk '{print $1}')
        webui_service=$(oc get services | grep "rucio-ui" | awk '{print $1}')
        messenger_service=$(oc get services | grep "rucio-messenger" | awk '{print $1}')
        oc patch svc ${messenger_service} -p '{"spec":{"externalIPs":["'"$FNAL_RUCIO_EXT_MSG_IP"'"]}}'
        oc patch svc ${webui_service} -p '{"spec":{"externalIPs":["'"$FNAL_RUCIO_EXT_WEBUI_IP"'"]}}'
        oc patch svc ${server_service} -p '{"spec":{"externalIPs":["'"$FNAL_RUCIO_EXT_SERVER_IP"'"]}}'
        oc patch svc ${auth_server_service} -p '{"spec":{"externalIPs":["'"$FNAL_RUCIO_EXT_AUTH_IP"'"]}}'
        echo -e "\tServer: ${FNAL_RUCIO_EXT_SERVER_IP}"
        echo -e "\tAuth Server: ${FNAL_RUCIO_EXT_AUTH_IP}"
        echo -e "\tMessenger: ${FNAL_RUCIO_EXT_MSG_IP}"
        echo -e "\tWebui: ${FNAL_RUCIO_EXT_WEBUI_IP}"
    fi
fi

echo -e "**************** Openshift application rucio-$EXPERIMENT deployment successful ****************"
