# Environtment set up file for the AccelAI environment

export DOCKER_BUILDKIT=1
export FNAL_RUCIO_VERSION=1.23.12

if [ -z ${RUCIO_FNAL_DEV} ]; then
    export FNAL_RUCIO_VERSION_TAG="latest"
else
    export FNAL_RUCIO_VERSION_TAG=${FNAL_RUCIO_VERSION}
fi

# Make sure to set EXPERIMENT, FNAL_RUCIO_DIR, FNAL_EXP_RUCIO_CERT, FNAL_EXP_RUCIO_KEY, FNAL_EXP_RUCIO_CA_BUNDLE
export EXPERIMENT=accelai
export FNAL_RUCIO_DIR=/nashome/b/bjwhite/dev/rucio/rucio-fnal

# Only the filenames are needed. The files should be resident in $FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export FNAL_EXP_RUCIO_CERT=accelai-rucio.okd.fnal.gov-cert.pem
export FNAL_EXP_RUCIO_KEY=accelai-rucio.okd.fnal.gov-key.pem
export FNAL_EXP_RUCIO_CA_BUNDLE=ca_bundle.pem
