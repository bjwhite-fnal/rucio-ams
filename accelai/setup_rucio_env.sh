# Environtment set up file for the icarus environment

export DOCKER_BUILDKIT=1
export FNAL_RUCIO_VERSION=1.23.4

# Make sure to set EXPERIMENT, FNAL_RUCIO_DIR, FNAL_EXP_RUCIO_CERT, FNAL_EXP_RUCIO_KEY, FNAL_EXP_RUCIO_CA_BUNDLE, FNAL_EXP_RUCIO_CERT_KEY_COMBINED
export EXPERIMENT=accelai
export FNAL_RUCIO_DIR=/cloud/login/bjwhite/dev/rucio/rucio-fnal

# Only the filenames are needed. The files should be resident in $FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export FNAL_EXP_RUCIO_CERT=accelai-rucio.okd.fnal.gov-cert.pem
export FNAL_EXP_RUCIO_KEY=accelai-rucio.okd.fnal.gov-key.pem
export FNAL_EXP_RUCIO_CA_BUNDLE=ca_bundle.pem