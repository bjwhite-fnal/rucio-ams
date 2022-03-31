# Environtment set up file for the int testing "experiment" 
export RUCIO_FNAL_DEV=true

# I love parallel builds!
export DOCKER_BUILDKIT=1
#export RUCIO_AMS_VERSION=1.23.11.post2
#export RUCIO_AMS_VERSION=1.23.14
#export RUCIO_AMS_VERSION=1.24.5.post1
#export RUCIO_AMS_VERSION=1.25.7
#export RUCIO_AMS_VERSION=1.26.1.post1
#export RUCIO_AMS_VERSION=1.26.5
#export RUCIO_AMS_VERSION=1.26.6
#export RUCIO_AMS_VERSION=1.26.7
#export RUCIO_AMS_VERSION=1.26.8
export RUCIO_AMS_VERSION=1.26.9

if [ -z ${RUCIO_FNAL_DEV} ]; then
    export RUCIO_AMS_VERSION_TAG=${RUCIO_AMS_VERSION}
else
    export RUCIO_AMS_VERSION_TAG="latest"
fi

# Make sure to set EXPERIMENT, RUCIO_AMS_DIR, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE
# Optionally set RUCIO_AMS_EXT_SERVER_IP, RUCIO_AMS_EXT_AUTH_IP, RUCIO_AMS_EXT_WEBUI_IP, RUCIO_AMS_EXT_MSG_IP
# For AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE only the filenames are needed.
#   The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export EXPERIMENT=int
export RUCIO_AMS_DIR=/nashome/b/bjwhite/dev/rucio/rucio-fnal
export AMS_RUCIO_CERT=int-rucio.okd.fnal.gov-cert.pem
export AMS_RUCIO_KEY=int-rucio.okd.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem

#export RUCIO_AMS_EXT_SERVER_IP=131.225.218.134
#export RUCIO_AMS_EXT_AUTH_IP=131.225.218.147
#export RUCIO_AMS_EXT_WEBUI_IP=131.225.218.148
#export RUCIO_AMS_EXT_MSG_IP=131.225.218.149
