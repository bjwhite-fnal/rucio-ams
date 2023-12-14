# Environtment set up file for the ICARUS environment
export DOCKER_BUILDKIT=1
export RUCIO_AMS_VERSION=1.29.12

# Make sure to set EXPERIMENT, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE

# Only the filenames are needed. The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export AMS_RUCIO_CERT=icarus-rucio.fnal.gov-cert.pem
export AMS_RUCIO_KEY=icarus-rucio.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem

export RUCIO_AMS_EXT_SERVER_IP=131.225.218.171
export RUCIO_AMS_EXT_AUTH_IP=131.225.218.170
export RUCIO_AMS_EXT_MSG_IP=131.225.218.168
export RUCIO_AMS_EXT_WEBUI_IP=131.225.218.169
