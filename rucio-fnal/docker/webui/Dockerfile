# Dockerfile for creating a Rucio WebUI container for use with FNAL Rucio deployments

ARG rucio_version 
FROM rucio/rucio-ui:release-$rucio_version

# This is just debug stuff
RUN yum install -y patch net-tools vim less

# These config files do not need to be added currently as they don't differ from
#   the official image
#ADD ./rucio.cfg.j2 /tmp/
#ADD ./rucio.conf.j2 /tmp/


ADD permissions/ /opt/rucio/permissions
ADD ./docker-entrypoint.sh / 
ADD ./configure_rucio_environment.sh /

# Patches
#ADD patches/* /tmp/patches/
#RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi
