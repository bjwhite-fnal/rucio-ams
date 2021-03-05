# Fermilab Rucio Deployment Logrotate Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2021

FROM centos:7

RUN yum install -y logrotate

ADD ./logrotate.conf /etc/logrotate.d/logrotate.conf
ADD ./docker-entrypoint.sh /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
