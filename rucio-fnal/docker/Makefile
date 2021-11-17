
# Use this to control building and pushing of Docker images in a significantly less ugly fashion.
#

# Top level Makefile commands (also can build individual images with `make build-<server|daemons|webui|etc...>`)
push-all:
	$(push-server-cmd)
	$(push-daemons-cmd)
	$(push-cache-cmd)
	$(push-messenger-cmd)
	$(push-webui-cmd)
	$(push-fts-cron-cmd)
	$(push-filebeat-cmd)
	$(push-logstash-cmd)
	$(push-logrotate-cmd)
	$(push-statsd-cmd)

build-all:
	$(build-server-cmd)
	$(build-daemons-cmd)
	$(build-cache-cmd)
	$(build-messenger-cmd)
	$(build-webui-cmd)
	$(build-fts-cron-cmd)
	$(build-filebeat-cmd)
	$(build-logstash-cmd)
	$(build-logrotate-cmd)
	$(build-statsd-cmd)

build-all-nc:
	$(build-server-nc-cmd)
	$(build-daemons-nc-cmd)
	$(build-cache-nc-cmd)
	$(build-messenger-nc-cmd)
	$(build-webui-nc-cmd)
	$(build-fts-cron-nc-cmd)
	$(build-filebeat-nc-cmd)
	$(build-logstash-nc-cmd)
	$(build-logrotate-nc-cmd)
	$(build-statsd-nc-cmd)

# Image build command definitions
define build-statsd-cmd =
docker build -t rucio-statsd statsd
endef

define build-statsd-nc-cmd =
docker build --no-cache -t rucio-statsd statsd
endef

define build-autotransfer-cmd =
docker build -t rucio-autotransfer autotransfer 
endef

define build-autotransfer-nc-cmd =
docker build --no-cache -t rucio-autotransfer autotransfer 
endef

define build-logrotate-cmd =
docker build -t rucio-logrotate logrotate
endef

define build-logrotate-nc-cmd =
docker build --no-cache -t rucio-logrotate logrotate
endef

define build-logstash-cmd =
docker build -t rucio-logstash logstash
endef

define build-logstash-nc-cmd =
docker build --no-cache -t rucio-logstash logstash
endef

define build-filebeat-cmd =
docker build -t rucio-filebeat filebeat
endef

define build-filebeat-nc-cmd =
docker build --no-cache -t rucio-filebeat filebeat
endef

define build-fts-cron-cmd =
docker build -t rucio-fts-cron fts-cron
endef

define build-fts-cron-nc-cmd =
docker build --no-cache -t rucio-fts-cron fts-cron
endef

define build-webui-cmd =
docker build -t rucio-webui --build-arg rucio_version=${FNAL_RUCIO_VERSION} webui
endef

define build-webui-nc-cmd =
docker build --no-cache -t rucio-webui --build-arg rucio_version=${FNAL_RUCIO_VERSION} webui
endef

define build-server-cmd =
docker build -t rucio-server --build-arg rucio_version=${FNAL_RUCIO_VERSION} server
endef

define build-server-nc-cmd =
docker build --no-cache -t rucio-server --build-arg rucio_version=${FNAL_RUCIO_VERSION} server	
endef

define build-daemons-cmd =
docker build -t rucio-daemons --build-arg rucio_version=${FNAL_RUCIO_VERSION} daemons
endef

define build-daemons-nc-cmd =
docker build --no-cache -t rucio-daemons --build-arg rucio_version=${FNAL_RUCIO_VERSION} daemons
endef

define build-cache-cmd =
docker build -t rucio-cache cache
endef

define build-cache-nc-cmd =
docker build --no-cache -t rucio-cache cache
endef

define build-messenger-cmd =
docker build -t rucio-messenger messenger
endef

define build-messenger-nc-cmd =
docker build --no-cache -t rucio-messenger messenger
endef

# Image build command declarations
build-statsd:
	$(build-statsd-cmd)

build-statsd-nc:
	$(build-statsd-nc-cmd)

build-autotransfer:
	$(build-autotransfer-cmd)

build-autotransfer-nc:
	$(build-autotransfer-nc-cmd)

build-logrotate:
	$(build-logrotate-cmd)

build-logrotate-nc:
	$(build-logrotate-nc-cmd)

build-logstash:
	$(build-logstash-cmd)

build-logstash-nc:
	$(build-logstash-nc-cmd)

build-filebeat:
	$(build-filebeat-cmd)

build-filebeat-nc:
	$(build-filebeat-nc-cmd)

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

# Image push command definitions
define push-statsd-cmd =
	docker tag rucio-statsd imageregistry.fnal.gov/rucio-fnal/fnal-rucio-statsd:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-statsd:${FNAL_RUCIO_VERSION_TAG}
endef

define push-autotransfer-cmd =
	docker tag rucio-autotransfer imageregistry.fnal.gov/rucio-fnal/fnal-rucio-autotransfer:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-autotransfer:${FNAL_RUCIO_VERSION_TAG}
endef

define push-logrotate-cmd =
	docker tag rucio-logrotate imageregistry.fnal.gov/rucio-fnal/fnal-rucio-logrotate:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-logrotate:${FNAL_RUCIO_VERSION_TAG}
endef

define push-logstash-cmd =
	docker tag rucio-logstash imageregistry.fnal.gov/rucio-fnal/fnal-rucio-logstash:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-logstash:${FNAL_RUCIO_VERSION_TAG}
endef

define push-filebeat-cmd =
	docker tag rucio-filebeat imageregistry.fnal.gov/rucio-fnal/fnal-rucio-filebeat:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-filebeat:${FNAL_RUCIO_VERSION_TAG}
endef

define push-fts-cron-cmd =
	docker tag rucio-fts-cron imageregistry.fnal.gov/rucio-fnal/fnal-rucio-fts-cron:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-fts-cron:${FNAL_RUCIO_VERSION_TAG}
endef

define push-webui-cmd =
	docker tag rucio-webui imageregistry.fnal.gov/rucio-fnal/fnal-rucio-webui:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-webui:${FNAL_RUCIO_VERSION_TAG}
endef


define push-server-cmd =
	docker tag rucio-server imageregistry.fnal.gov/rucio-fnal/fnal-rucio-server:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-server:${FNAL_RUCIO_VERSION_TAG}
endef


define push-daemons-cmd =
	docker tag rucio-daemons imageregistry.fnal.gov/rucio-fnal/fnal-rucio-daemons:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-daemons:${FNAL_RUCIO_VERSION_TAG}
endef

define push-cache-cmd =
	docker tag rucio-cache imageregistry.fnal.gov/rucio-fnal/fnal-rucio-cache:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-cache:${FNAL_RUCIO_VERSION_TAG}
endef

define push-messenger-cmd =
	docker tag rucio-messenger imageregistry.fnal.gov/rucio-fnal/fnal-rucio-messenger:${FNAL_RUCIO_VERSION_TAG}
	docker push imageregistry.fnal.gov/rucio-fnal/fnal-rucio-messenger:${FNAL_RUCIO_VERSION_TAG}
endef

# Image push command declarations
push-statsd:
	$(push-statsd-cmd)

push-autotransfer:
	$(push-autotransfer-cmd)

push-logrotate:
	$(push-logrotate-cmd)

push-logstash:
	$(push-logstash-cmd)

push-filebeat:
	$(push-filebeat-cmd)

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
