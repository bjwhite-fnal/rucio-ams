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

# Temporary. Adds functionality which was not present for configuring HTTPD log dir in the server
# Remove this file once you can set the server HTTPD log dir based on $RUCIO_HTTPD_LOG_DIR
ADD rucio.conf.j2 /tmp

VOLUME /etc/grid-security

ENTRYPOINT ["/start-server.sh"]
