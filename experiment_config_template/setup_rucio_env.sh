# Environtment set up file for the DUNE environment


# Make sure to set EXPERIMENT, FNAL_RUCIO_DIR, FNAL_EXP_RUCIO_CERT, FNAL_EXP_RUCIO_KEY, FNAL_EXP_RUCIO_CA_BUNDLE
export EXPERIMENT=REPLACE_ME_EXPERIMENT
export FNAL_RUCIO_DIR=< Path to top of rucio-fnal git repository >

# Only the filenames are needed. The files should be resident in $FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR/certs 
export FNAL_EXP_RUCIO_CERT=< CERTIFICATE FILE NAME >
export FNAL_EXP_RUCIO_KEY=< KEY FILE NAME >
export FNAL_EXP_RUCIO_CA_BUNDLE=ca_bundle.pem
export FNAL_EXP_RUCIO_CERT_KEY_COMBINED=< Probably need to concat the cert + key yourself, filename goes here >
