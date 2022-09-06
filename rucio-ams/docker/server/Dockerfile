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
RUN pip3 install metacat remote-pdb

# Add FNAL specific files
ADD rucio.cfg.j2 /tmp
ADD alembic.ini.j2 /tmp
ADD gacl /opt/rucio/etc/
ADD configure_server_log_location.sh /
ADD start-server.sh /
ADD permissions/ /opt/rucio/permissions/fermilab

#tmp
#ADD rucio.conf.j2 /tmp/

VOLUME /etc/grid-security

ENTRYPOINT ["/start-server.sh"]
