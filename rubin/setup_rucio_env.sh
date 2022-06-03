# Environtment set up file for the Rubin environment

export DOCKER_BUILDKIT=1
export RUCIO_AMS_VERSION=1.26.9

if [ -z ${RUCIO_AMS_DEV} ]; then
    export RUCIO_AMS_VERSION_TAG=${RUCIO_AMS_VERSION}
else
    export RUCIO_AMS_VERSION_TAG="latest"
fi

# Make sure to set EXPERIMENT, RUCIO_AMS_DIR, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE
export EXPERIMENT=rubin
export RUCIO_AMS_DIR=/sdf/home/b/bjwhite/rucio-ams

# Only the filenames are needed. The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export AMS_RUCIO_CERT=hostcert.pem
export AMS_RUCIO_KEY=hostkey.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem

#export RUCIO_AMS_EXT_SERVER_IP=131.225.218.128
#export RUCIO_AMS_EXT_AUTH_IP=131.225.218.150
#export RUCIO_AMS_EXT_MSG_IP=131.225.218.152
#export RUCIO_AMS_EXT_WEBUI_IP=131.225.218.151
