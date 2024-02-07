# Fermilab Rucio Init Docker Image Specification
# 
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020
# - Dennis Lee, <dylee@fnal.gov>, 2023

ARG rucio_version
FROM rucio/rucio-init:release-${rucio_version}

RUN yum install -y gridsite \
    patch \
    net-tools \
    telnet \
    less
RUN pip3 install metacat remote-pdb

# Add FNAL specific files
ADD permissions/ /opt/rucio/permissions/fermilab

VOLUME /etc/grid-security

COPY bootstrap.py /tmp

CMD ["/docker-entrypoint.sh"]
