
# rucio-ams 
## Cluster-based Rucio Deployment Framework 
### Scientific Data Management
#### Brandon White
bjwhite@fnal.gov

Use this to deploy Rucio for an experiment. First source an experiments environment file and deploy the application suite to the cluster with the experiment generic rucio-ams framework.
In particular please make sure that the following are set by the sourcing of the appropriate experiment environment file, usually setup_rucio_env.sh in the experiment configuration bundle:
~~~~
    EXPERIMENT: Name of the experiment that configuration files are being generated for. Used when generating helm deployment configurations.
    RUCIO_AMS_DIR: Set to the top level directory of the rucio-ams repository (i.e. the directory this README resides in). Enables configuration files to be found in the directory structure detailed below.
    AMS_RUCIO_CERT: Certificate for service authentication.
    AMS_RUCIO_KEY: Key for service authentication.
    AMS_RUCIO_CA_BUNDLE: CA certificates for service authentication.
    AMS_RUCIO_CERT_KEY_COMBINED: Certificate and key concatenated. Needed for the Web UI.
    RUCIO_AMS_DEV: Automatically use the latest versions of all images, rather than repecting RUCIO_AMS_VERSION for image tagging upon image pulls from the repository.
    RUCIO_AMS_VERSION: Use this when building rucio-ams-* images to select the desired Rucio version for installation into the image.
    RUCIO_AMS_EXT_SERVER_IP: Specifies the external IPV4 address of the server service deployment
    RUCIO_AMS_EXT_AUTH_IP: Specifies the external IPV4 address of the auth server service deployment
    RUCIO_AMS_EXT_WEBUI_IP: Specifies the external IPV4 address of the webui service deployment
    RUCIO_AMS_EXT_MSG_IP: Specifies the external IPV4 address of the messenger service deployment
~~~~

## Before Deployment To-Do List
~~~~
    0. Have a database created for the new deployment to use. (Duh)
    1. Create rucio-<experiment> project in OKD / Have a Kubernetes cluster or vCluster configured for the application
    2. Make sure you have the service certificate and private key for the Rucio service, with alternate names defined for the various services (webui, msg, auth)
    3. Ensure that the certificate is registered in a your installation's federated identity system (e.g. FERRY/VOMS) to the account that is to own/manage data on the RSEs
    4. Edit <experiment>/setup_rucio_env.sh to set the required environment variables appropriately as described above
    5. Have the cluster administrators allocate an external IPv4 address and set up DNS resolution for the deployment
    6. Have the cluster administrators create the `useroot` account for the deployment to use in order to allow the containers to run as root
    7. Have the cluster administrators create the following DNS records (ensure that the name/altnames specified in your service certificate match the following):
        <experiment>-rucio.okd.fnal.gov
        auth-<experiment>-rucio.okd.fnal.gov
        msg-<experiment>-rucio.okd.fnal.gov
        webui-<experiment>-rucio.okd.fnal.gov
~~~~

Source the setup_rucio_env.sh file at the top of the target experiment's configuration tree to configure the environment.
Use deploy-rucio.sh to deploy services onto the OKD cluster after the environment is configured appropriately as described above.
Use undeploy-rucio.sh to remove everything (Services, Pods, Routes, Persistent Volumes and Claims, etc..).

The Rucio source code may be patched when the images are built by placing patch files into one of two locations: $RUCIO_AMS_DIR/rucio-ams/docker/[server,daemon]/patches

## EXAMPLE DIRECTORY STRUCTURE FOR AN EXPERIMENT:
~~~~
    dune
    ├── certs                               < Experiment specific certificate, key, cert/key concatenated, and CA certificate bundle. >
    │   ├── ca_bundle.pem
    │   ├── rucio.fnal.gov_cert.pem
    │   └── rucio.fnal.gov_key.pem
    ├── helm
    │   ├── cache
    │   │   └── values.yaml
    │   ├── filebeat 
    │   │   └── values.yaml
    │   ├── logstash 
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
    │   │   └── values.yaml                 < Server configuration specific values >
    │   └── webui
    │       └── values.yaml
    ├── patches
    └── setup_dune_rucio_env.sh             < Export the needed environment variables for experiment setup >
~~~~

Directories named certs/ and secret/ will not be committed to the repository according to the default .gitignore file.

When building new container images, setup the the experiment's deployment environment (setup_rucio_env.sh). Use hard links or manual copy to place the permissions-fnal/ Python files into the server, daemons, and WebUI Docker build contexts via a /permissions in each directory.
TODO: This will become obsolete once it is set up such that the policy packages will be `git clone`d into the images at build time.

Use the Makefile in rucio-ams/docker to build and push Docker images. See the Makefile for info on commands.

## Using custom Policy Packages
Rucio policy package directories must be added to the PYTHONPATH search variable inside of the Rucio containers. (See https://github.com/rucio/rucio/blob/master/doc/source/policy_packages.rst for details) 
Make sure to set the environment variable `policy_pkg_dir` in the containers (using the optional_config section in the Helm values files of the server/daemon/webui/etc... If this variable is set, the value will be prepended
to the value of PYTHONPATH inside the container.

Finally, to configure which policy package should be used for a given Rucio deployment, make sure to specify under the `config` section the following settings for policies:
```
policy:
  package: fermilab.<generic|dune|etc...>
  support: "Brandon White <bjwhite@fnal.gov>"
```
Do NOT specify the permission and schema options that you might see in the Rucio upstream... This prevents the correct policy from being imported.

## Note about Reaper certificates
The Reaper needs a full directory of certificates as opposed to a concatenated PEM. This should be handled by this framework, but it is worth keeping in mind.

## Enabling Metrics for `rucio-server`
When enabling metrics in `server/values.yaml`. there are a few gotchas to take note of.

### Setting `config.monitor.enable_metrics` to `false`
If this is enabled, the `prometheus_client` in `rucio/core/monitor.py` will try to start the HTTP server using `METRICS_PORT`. This causes issues in the `httpd`. In `rucio.conf`, multiple workers are enabled

### Setting `optional_config.rucio_metrics_port` to `8080`
    * Sets the `RUCIO_METRICS_PORT` environment variable
    * Enables the `httpd` `rucio.conf` setting that starts WSGI server for `metrics` endpoint

### Set `monitoring.enabled` to `false` 
    * We cannot do this: `servicemonitors.monitoring.coreos.com is forbidden: User <user> cannot create resource "servicemonitors" in API group "monitoring.coreos.com" in the namespace "monitoring"`
