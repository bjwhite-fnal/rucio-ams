# Changelog

## 1.26.9 to 1.26.13
* Disable `enable_metrics` in `server/values.yaml`
  * Multiprocessing not yet implemented
  * Have not yet figured out to work with `httpd`


## 1.26.13 to 1.27.11
### Main Changes
* Prepare values for OKD 4
  * Uses OKD 4 endpoints
  * Added proxy url config for webui
* Updated API versions for OKD 4
  * CronJob: `batch/v1beta1` to `batch/v1`
  * Deployment: `apps/v1beta2` to `apps/v1`
  * Route: `v1` to `route.openshift.io/v1`
* Removed custom `rucio.cfg.j2` in favor of using `merge_rucio_configs.py` in Dockerfiles
  * Images:
    * `daemons`
* `helm-charts` now at `rucio-daemons-1.27.4`

### Docker Images
* `messenger`
  * `EXPOSE 443`
  * Removed unused `EXPOSE 61614`
    * `messenger` uses port 443
  * Modified `docker-entrypoint.sh` so that `configure-rabbitmq.sh` is consistently created
    * Previous inline `envsubst` would randomly cause `configure-rabbitmq.sh` to be an empty file
* `webui`
  * Removed the script that set `RUCIO_PROXY` and `RUCIO_AUTH_PROXY`

### Experiment Helm Values
* `daemons`
  * Removed `config.common` section (Causing null problems in rucio.cfg)
  * Under `config`, moved `cache_*` and `hermes_*` configuretion from under `config.messaging` to `messaging-cache` and `messaging-hermes` sections, respectively
  * Changed defined messaging broker url to use internal names
    * `msg-int-rucio.fnal.gov` to `rucio-messenger`
* `server`
  * Removed `config.common` section (Causing null problems in rucio.cfg)
  * Added `enable_status: "False"` under `httpd_config`
* `web-ui`
  * Added proxy url configuration (`proxy.rucioProxy` and `proxy.rucioAuthProxy`)
  * Moved bootstrap values under `config` section

### Helper Scripts
* `rucio-env`
  * A more generic environment similar to Python venv `source venv/bin/activate`
  * Experiment specific varibles are defined in `setup_rucio_env.sh`
  * Displays `rucio-$EXPERIMENT $RUCIO_AMS_VERSION_TAG` in terminal
  * Sourcing also adds the `bin` directory to `PATH`
* get-logs
  * Retrieves all logs based on app label
* Able to use `deploy` and `undeploy` anywhere as long as `rucio-env` is sourced

### Other notes
* Update `kubectl` to 1.23.5 for OKD4
* Update `oc` to v4.2.0 for OKD4
* Author tag is added to docker images in Makefile
  * Easier to filter out in image registry
* Upgrade database schema `db/1.27.4.sql`
  * `alembic_version 739064d31565 -> 9a45bc4ea66d`
  * Added `virtual_placements` table
  * Upgraded using `psql <database uri> < 1.27.4.sql`
  * File was created through alembic script in official `rucio/rucio` repository

## 1.27.11 to 1.28.7
### Docker Images
* `webui`
  * Removed custom `rucio.conf.j2` from image in favor of using existing one
* `server`
  * Updated `rucio.conf.j2` to match existing one in the `rucio-server` image
  * However, `rucio.conf.j2` is also removed from image in favor of using existing one
* `permissions-fnal`
  * Added the `session=None` kwarg in the `generic/permission.py` has_permission` function
* `daemons`
  * Added `rsync` to image

### Experiment Helm Values
* Update `ftshosts` for `conveyor` config to new names

### Misc
* Ensure that RSE fts urls are correct (`rucio-admin rse info`)
* Setting the `RUCIO_AMS_VERSION_TAG` can now be done in `rucio-env`
* Upgrade database schema `db/1.28.7.sql`
  * Ensure that `third_party_copy_read` and `third_party_copy_write` columns are set correctly in `rse_protocols` table in database after upgrade


## 1.28.7 to 1.29.3.post1
### Changes
* `daemons/values.yaml`
  * Changed `delay` to `sleepTime`
* Upgrade `helm-charts` to `rucio-ui-1.29.1`
* Upgrade database schema `db/1.29.0.sql`

## 1.29.7.post, helm-charts `rucio-daemons-1.29.7`
### `replica-recoverer` daemon
* Set `replicaRecovererCount: 1` in `$EXPERIMENT/helm/daemons/values.yaml`
* Add `replicaRecoverer` section to `$EXPERIMENT/helm/daemons/values.yaml`
  * Placed similar values to other daemons to config
* Include `suspicious_replica_recoverer.json` in the `$RUCIO_AMS/$EXPERIMENT/` directory
  * This gets added as `rucio-$EXPERIMENT-suspicious-replica-recoverer-input` secret
* Add the secret by adding this to `$EXPERIMENT/helm/daemons/values.yaml`
```
additionalSecrets:
  suspicious-replica-recoverer-input:
    secretName: suspicious-replica-recoverer-input
    mountPath: /opt/rucio/etc/suspicious_replica_recoverer.json
    subPath: suspicious_replica_recovere.json
```
* Set attribute `enable_suspicious_file_recovery` to be `true` on target RSE
```
$ rucio-admin rse set-attribute --rse DCACHE_BJWHITE_START --key enable_suspicious_file_recovery --value true
```

## Miscellaneous
* Ensure OKD IP Addresses are added to `pg_hba.conf` on the databases.
#### Enabling Metrics for `rucio-server` in OKD Cluster
* In `server/values.yaml`
  * Set `config.monitor.enable_metrics` to `false`
    * Prevents `prometheus_client` from starting HTTP servers that vie for same port
    * Causes issues with httpd and prometheus’ start_http_server
    * Prometheus start_http_server is called for every worker, which causes error when all are fighting for same METRICS_PORT
  * Set `optional_config.rucio_metrics_port` to `8080`
    * Cannot be the same as the main server port (i.e. 443)
    * Sets the `RUCIO_METRICS_PORT` environment variable
    * Enables the `httpd` `rucio.conf` setting that starts WSGI server for `metrics` endpoint
  * Set `monitoring.enabled` to `false` 
    * We cannot do this: `servicemonitors.monitoring.coreos.com is forbidden: User <user> cannot create resource "servicemonitors" in API group "monitoring.coreos.com" in the namespace "monitoring"`
