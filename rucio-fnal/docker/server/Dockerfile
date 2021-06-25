# Fermilab Rucio Server Docker Image Specification
# 
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020

ARG rucio_version
FROM rucio/rucio-server:release-${rucio_version}

RUN yum install -y gridsite \
    patch \
    net-tools \
    telnet \
    less
RUN pip3 install remote-pdb
RUN mv /etc/httpd/conf.d/zgridsite.conf /etc/httpd/conf.d/zgridsite.conf-hide

# Add FNAL specific files
ADD alembic.ini.j2 /tmp
ADD gacl /opt/rucio/etc/
ADD configure_server_log_location.sh /
ADD start-server.sh /
ADD permissions/ /opt/rucio/permissions/fermilab

# TEMPORARY CONFIG ADD FOR UNTIL THE STUFF GETS BUILT INTO THE REAL CONTAINERS 
ADD rucio.cfg.j2 /tmp

# Patches
ADD patches/* /tmp/patches/
RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

VOLUME /etc/grid-security

ENTRYPOINT ["/start-server.sh"]
