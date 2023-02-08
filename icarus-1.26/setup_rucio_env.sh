# Environtment set up file for the icarus environment

export DOCKER_BUILDKIT=1
#export RUCIO_AMS_VERSION=1.23.14
#export RUCIO_AMS_VERSION=1.26.5
#export RUCIO_AMS_VERSION=1.26.7
#export RUCIO_AMS_VERSION=1.26.8
export RUCIO_AMS_VERSION=1.26.9

if [ -z ${RUCIO_AMS_DEV} ]; then
    export RUCIO_AMS_VERSION_TAG=${RUCIO_AMS_VERSION}
else
    export RUCIO_AMS_VERSION_TAG="latest"
fi

# Make sure to set EXPERIMENT, RUCIO_AMS_DIR, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE
export EXPERIMENT=icarus
export RUCIO_AMS_DIR=/nashome/b/bjwhite/dev/rucio/rucio-ams

# Only the filenames are needed. The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export AMS_RUCIO_CERT=icarus-rucio.okd.fnal.gov-cert.pem
export AMS_RUCIO_KEY=icarus-rucio.okd.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem