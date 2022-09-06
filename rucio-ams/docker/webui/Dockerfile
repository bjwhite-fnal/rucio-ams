# Dockerfile for creating a Rucio WebUI container for use with FNAL Rucio deployments

ARG rucio_version 
FROM rucio/rucio-ui:release-$rucio_version

RUN yum install -y metacat patch net-tools vim less

ADD permissions/ /opt/rucio/permissions/fermilab
ADD ./docker-entrypoint.sh / 

# Patches
#ADD patches/* /tmp/patches/
#RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi
