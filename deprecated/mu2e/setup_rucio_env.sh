# Environtment set up file for the Mu2e environment
export DOCKER_BUILDKIT=1
export RUCIO_AMS_VERSION=1.29.12

# Make sure to set EXPERIMENT, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE

# Only the filenames are needed. The files should be resident in ${AMS_RUCIO_DEPLOYMENT_CONF_DIR}/certs 
export AMS_RUCIO_CERT=mu2e-rucio.fnal.gov-cert.pem
export AMS_RUCIO_KEY=mu2e-rucio.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem

export RUCIO_AMS_EXT_SERVER_IP=131.225.218.181
export RUCIO_AMS_EXT_AUTH_IP=131.225.218.180
export RUCIO_AMS_EXT_MSG_IP=131.225.218.178
export RUCIO_AMS_EXT_WEBUI_IP=131.225.218.179
