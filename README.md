
# Bridle: Fermilab Rucio Deployment Management
## Scientific Data Management
### Brandon White
### bjwhite@fnal.gov

Use this to deploy Rucio for an experiment. First source an experiments environment file and deploy with the experiment generic rucio-fnal framework.
In particular please make sure that the following are set by the sourcing of the environment file:
~~~~
    EXPERIMENT: Name of the experiment that configuration files are being generated for.
    FNAL_RUCIO_DIR: Set to the top level directory of the rucio-fnal repository (i.e. the directory this README resides in). Enables configuration files to be found in the directory structure detailed below.
    FNAL_EXP_RUCIO_CERT: Certificate for service authentication.
    FNAL_EXP_RUCIO_KEY: Key for service authentication.
    FNAL_EXP_RUCIO_CA_BUNDLE: CA certificates for service authentication.
    FNAL_EXP_RUCIO_CERT_KEY_COMBINED: Certificate and key concatenated. Needed for the Web UI.
    FNAL_RUCIO_VERSION: Use this when building fnal-rucio-* images to select the desired Rucio version for installation into the image. 
~~~~

Use deploy-rucio.sh to deploy services onto the OKD cluster after the environment is configured appropriately as described above.
Use undeploy-rucio.sh to remove them.

The Rucio code may be monkey patched at image build time by placing patch files into one of two locations: $FNAL_RUCIO_DIR/rucio-fnal/docker/[server,daemon]-base/patches

## EXAMPLE DIRECTORY STRUCTURE FOR AN EXPERIMENT:
~~~~
    dune
    ├── certs                               < Experiment specific certificate, key, cert/key concatenated, and CA certificate bundle. >
    │   ├── ca_bundle.pem
    │   ├── rucio.fnal.gov_cert.pem
    │   ├── rucio.fnal.gov_combined.pem
    │   └── rucio.fnal.gov_key.pem
    ├── helm
    │   ├── cache
    │   │   └── values.yaml
    │   ├── daemons
    │   │   └── values.yaml                 < Daemon configuration specific values > 
    │   ├── messenger
    │   │   └── values.yaml
    │   ├── osg_authentication
    │   │   └── values.yaml
    │   ├── secret
    │   │   └── config.yaml                 < Secret information such as DB connection string. >
    │   ├── server
    │   │   └── values.yaml
    │   └── webui
    │       └── values.yaml                 < Server configuration specific values >
    ├── patches
    └── setup_dune_rucio_env.sh             < Export the needed environment variables for experiment setup >
~~~~

Directories named cert/ and secret/ will not be committed to the repository according to the default .gitignore file.
