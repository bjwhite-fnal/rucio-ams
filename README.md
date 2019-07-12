
# Fermilab Rucio Deployment System
## Scientific Data Management
### Brandon White
### bjwhite@fnal.gov

Use this to deploy Rucio for an experiment. First source an experiments environment file and deploy with the experiment generic rucio-fnal framework.
In particular please make sure that the following are set by the sourcing of the environment file:
~~~~
    FNAL_EXP_RUCIO_DEPLOYMENT_CONF_DIR: The directory that the server.yaml and daemons.yaml will be saved in upon generation
    RUCIO_HELM_TEMPLATE_DIR: Location of the experiment specific YAML files that contain values for substitution into Rucio configuration files
    EXPERIMENT: Name of the experiment that configuration files are being generated for
~~~~

Use deploy-rucio.sh to deploy things onto the OKD cluster.
Use undeploy-rucio.sh to remove them.

## EXAMPLE DIRECTORY STRUCTURE FOR AN EXPERIMENT:
~~~~
    dune
    ├── certs                               < Experiment specific certificate, key, and CA certificate bundle. ( certs/ will not be committed to the repository ) >
    │   ├── ca_bundle.pem
    │   ├── rucio-dev.fnal.gov-cert.pem
    │   ├── rucio-dev.fnal.gov-key.pem
    ├── helm
    │   ├── daemons
    │   │   └── values.yaml                 < Daemon configuration specific values > 
    │   ├── secret
    │   │   └── config.yaml                 < Secret information such as DB connection string. ( secret/ will not be committed to the repository ) >
    │   └── server
    │       └── values.yaml                 < Server configuration specific values >
    └── setup_dune_rucio_env.sh
~~~~
