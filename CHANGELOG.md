# Changelog

## 1.26.9 to 1.26.13
---
* Disable `enable_metrics` in `server/values.yaml`
  * Multiprocessing not yet implemented
  * Have not yet figured out to work with `httpd`


## 1.26.13 to 1.27.11
---
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
---
* Ensure that `third_party_copy_read` and `third_party_copy_write` columns are set correctly in `rse_protocols`
* Ensure that RSE fts urls are correct
