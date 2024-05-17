
# Use this to control building and pushing of container images in a significantly less ugly fashion.
#
#
# check to see if podman is installed and running; otherwise, use docker
ifeq ($(shell command podman version 2> /dev/null),)
	CMD=docker
else
	CMD=podman
endif

# Top level Makefile commands (also can build individual images with `make build-<server|daemons|webui|etc...>`)
push-all:
	$(push-server-cmd)
	$(push-daemons-cmd)
	$(push-cache-cmd)
	$(push-messenger-cmd)
	$(push-webui-cmd)
	$(push-fts-cron-cmd)
	$(push-statsd-cmd)
	$(push-prometheus-cmd)

build-all:
	$(build-server-cmd)
	$(build-daemons-cmd)
	$(build-cache-cmd)
	$(build-messenger-cmd)
	$(build-webui-cmd)
	$(build-fts-cron-cmd)
	$(build-statsd-cmd)
	$(build-prometheus-cmd)

build-all-nc:
	$(build-server-nc-cmd)
	$(build-daemons-nc-cmd)
	$(build-cache-nc-cmd)
	$(build-messenger-nc-cmd)
	$(build-webui-nc-cmd)
	$(build-fts-cron-nc-cmd)
	$(build-statsd-nc-cmd)
	$(build-prometheus-nc-cmd)

test:
	$(CMD) version

# Image build command definitions
define build-prometheus-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-prometheus prometheus 
endef

define build-statsd-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-statsd statsd
endef

define build-logrotate-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-logrotate logrotate
endef

define build-logrotate-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-logrotate logrotate
endef

define build-logstash-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-logstash logstash
>>>>>>> Debugging
endef

define build-prometheus-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-prometheus prometheus
endef

define build-statsd-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-statsd statsd
endef

define build-fts-cron-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-fts-cron fts-cron
endef

define build-fts-cron-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-fts-cron fts-cron
endef

define build-webui-cmd =
-rm -rf webui/permissions
cp -r permissions-fnal webui/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-webui --build-arg rucio_version=${RUCIO_AMS_VERSION} webui
-rm -rf webui/permissions
endef

define build-webui-nc-cmd =
-rm -rf webui/permissions
cp -r permissions-fnal webui/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-webui --build-arg rucio_version=${RUCIO_AMS_VERSION} webui
-rm -rf webui/permissions
endef

define build-server-cmd =
-rm -rf server/permissions
cp -r permissions-fnal server/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-server --build-arg rucio_version=${RUCIO_AMS_VERSION} server
-rm -rf server/permissions
endef

define build-server-nc-cmd =
-rm -rf server/permissions
cp -r permissions-fnal server/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-server --build-arg rucio_version=${RUCIO_AMS_VERSION} server	
-rm -rf server/permissions
endef

define build-daemons-cmd =
-rm -rf daemons/permissions
cp -r permissions-fnal daemons/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-daemons --build-arg rucio_version=${RUCIO_AMS_VERSION} daemons
-rm -rf daemons/permissions
endef

define build-daemons-nc-cmd =
-rm -rf daemons/permissions
cp -r permissions-fnal daemons/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-daemons --build-arg rucio_version=${RUCIO_AMS_VERSION} daemons
-rm -rf daemons/permissions
endef

define build-init-cmd =
-rm -rf init/permissions
cp -r permissions-fnal init/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-init --build-arg rucio_version=${RUCIO_AMS_VERSION} init
-rm -rf init/permissions
endef

define build-init-nc-cmd =
-rm -rf init/permissions
cp -r permissions-fnal init/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-init --build-arg rucio_version=${RUCIO_AMS_VERSION} init
-rm -rf init/permissions
endef

define build-client-cmd =
-rm -rf init/permissions
cp -r permissions-fnal init/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-client --build-arg rucio_version=${RUCIO_AMS_VERSION} client
-rm -rf init/permissions
endef

define build-client-nc-cmd =
-rm -rf init/permissions
cp -r permissions-fnal init/permissions
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-client --build-arg rucio_version=${RUCIO_AMS_VERSION} client
-rm -rf init/permissions
endef

define build-cache-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-cache cache
endef

define build-cache-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-cache cache
endef

define build-messenger-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" -t rucio-messenger messenger
endef

define build-messenger-nc-cmd =
$(CMD) build --label "maintainer=${RUCIO_BUILD_USER}" --no-cache -t rucio-messenger messenger
endef

# Image build command declarations
build-prometheus:
	$(build-prometheus-cmd)

build-prometheus-nc:
	$(build-prometheus-nc-cmd)

build-statsd:
	$(build-statsd-cmd)

build-statsd-nc:
	$(build-statsd-nc-cmd)

build-fts-cron:
	$(build-fts-cron-cmd)

build-fts-cron-nc:
	$(build-fts-cron-nc-cmd)

build-webui:
	$(build-webui-cmd)

build-webui-nc:
	$(build-webui-nc-cmd)

build-server:
	$(build-server-cmd)

build-server-nc:
	$(build-server-nc-cmd)

build-daemons:
	$(build-daemons-cmd)

build-daemons-nc:
	$(build-daemons-nc-cmd)

build-cache:
	$(build-cache-cmd)	

build-cache-nc:
	$(build-cache-nc-cmd)	

build-messenger:
	$(build-messenger-cmd)
	
build-messenger-nc:
	$(build-messenger-nc-cmd)	

build-init:
	$(build-init-cmd)
	
build-init-nc:
	$(build-init-nc-cmd)	

build-client:
	$(build-client-cmd)
	
build-client-nc:
	$(build-init-nc-cmd)	

# Image push command definitions
define push-prometheus-cmd =
	$(CMD) tag rucio-prometheus imageregistry.fnal.gov/rucio-ams/rucio-ams-prometheus:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-prometheus:${RUCIO_AMS_VERSION_TAG}
endef

define push-statsd-cmd =
	$(CMD) tag rucio-statsd imageregistry.fnal.gov/rucio-ams/rucio-ams-statsd:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-statsd:${RUCIO_AMS_VERSION_TAG}
endef

define push-fts-cron-cmd =
	$(CMD) tag rucio-fts-cron imageregistry.fnal.gov/rucio-ams/rucio-ams-fts-cron:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-fts-cron:${RUCIO_AMS_VERSION_TAG}
endef

define push-webui-cmd =
	$(CMD) tag rucio-webui imageregistry.fnal.gov/rucio-ams/rucio-ams-webui:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-webui:${RUCIO_AMS_VERSION_TAG}
endef

define push-server-cmd =
	$(CMD) tag rucio-server imageregistry.fnal.gov/rucio-ams/rucio-ams-server:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-server:${RUCIO_AMS_VERSION_TAG}
endef

define push-daemons-cmd =
	$(CMD) tag rucio-daemons imageregistry.fnal.gov/rucio-ams/rucio-ams-daemons:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-daemons:${RUCIO_AMS_VERSION_TAG}
endef

define push-client-cmd =
	$(CMD) tag rucio-client imageregistry.fnal.gov/rucio-ams/rucio-client:${RUCIO_AMS_VERSION_TAG}.fnal
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-client:${RUCIO_AMS_VERSION_TAG}.fnal
endef

define push-cache-cmd =
	$(CMD) tag rucio-cache imageregistry.fnal.gov/rucio-ams/rucio-ams-cache:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-cache:${RUCIO_AMS_VERSION_TAG}
endef

define push-messenger-cmd =
	$(CMD) tag rucio-messenger imageregistry.fnal.gov/rucio-ams/rucio-ams-messenger:${RUCIO_AMS_VERSION_TAG}
	$(CMD) push imageregistry.fnal.gov/rucio-ams/rucio-ams-messenger:${RUCIO_AMS_VERSION_TAG}
endef

# Image push command declarations
push-prometheus:
	$(push-prometheus-cmd)

push-statsd:
	$(push-statsd-cmd)

push-fts-cron:
	$(push-fts-cron-cmd)

push-webui:
	$(push-webui-cmd)

push-server:
	$(push-server-cmd)

push-daemons:
	$(push-daemons-cmd)

push-cache:
	$(push-cache-cmd)

push-messenger:
	$(push-messenger-cmd)

push-client:
	$(push-client-cmd)
