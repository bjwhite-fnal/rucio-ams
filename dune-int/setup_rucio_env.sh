# Environtment set up file for the DUNE environment
export RUCIO_AMS_DEV=true
export DOCKER_BUILDKIT=1
#export RUCIO_AMS_VERSION=1.22.7
#export RUCIO_AMS_VERSION=1.26.5
#export RUCIO_AMS_VERSION=1.26.7
#export RUCIO_AMS_VERSION=1.26.8
#export RUCIO_AMS_VERSION=1.29.3.post1
export RUCIO_AMS_VERSION=1.29.4

# Make sure to set EXPERIMENT, RUCIO_AMS_DIR, AMS_RUCIO_CERT, AMS_RUCIO_KEY, AMS_RUCIO_CA_BUNDLE
export RUCIO_AMS_DIR=/nashome/b/bjwhite/dev/rucio/rucio-ams

# Only the filenames are needed. The files should be resident in $AMS_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export AMS_RUCIO_CERT=dune-int-rucio.fnal.gov-cert.pem
export AMS_RUCIO_KEY=dune-int-rucio.fnal.gov-key.pem
export AMS_RUCIO_CA_BUNDLE=ca_bundle.pem
