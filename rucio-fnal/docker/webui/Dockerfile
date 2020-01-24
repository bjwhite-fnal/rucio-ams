# Dockerfile for creating a Rucio WebUI container for use with FNAL Rucio deployments

FROM rucio/rucio-ui


RUN yum install -y patch net-tools vim less

ADD ./rucio.cfg.j2 /tmp/
ADD ./rucio.conf.j2 /tmp/
ADD ./docker-entrypoint.sh / 
ADD ./configure_rucio_environment.sh /

# Patches
ADD patches/* /tmp/patches/
RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi
