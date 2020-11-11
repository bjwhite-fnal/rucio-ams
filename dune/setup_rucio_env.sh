# Environtment set up file for the DUNE environment

export DOCKER_BUILDKIT=1
export FNAL_RUCIO_VERSION=1.23.10

# Make sure to set EXPERIMENT, FNAL_RUCIO_DIR, FNAL_EXP_RUCIO_CERT, FNAL_EXP_RUCIO_KEY, FNAL_EXP_RUCIO_CA_BUNDLE, FNAL_EXP_RUCIO_CERT_KEY_COMBINED
export EXPERIMENT=dune
export FNAL_RUCIO_DIR=/cloud/login/bjwhite/dev/rucio/rucio-fnal

# Only the filenames are needed. The files should be resident in $FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export FNAL_EXP_RUCIO_CERT=dune-rucio.okd.fnal.gov-cert.pem
export FNAL_EXP_RUCIO_KEY=dune-rucio.okd.fnal.gov-key.pem
export FNAL_EXP_RUCIO_CA_BUNDLE=ca_bundle.pem
