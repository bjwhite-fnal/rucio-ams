# Copyright European Organization for Nuclear Research (CERN) 2017
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2017
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2018

FROM rucio-server-base

RUN yum install -y mod_ssl

RUN yum install -y gridsite

RUN rpm -i https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm
RUN yum install -y osg-ca-certs fetch-crl cronnie

RUN mv /etc/httpd/conf.d/zgridsite.conf /etc/httpd/conf.d/zgridsite.conf-hide

RUN echo "32 */6 * * * root ! /usr/sbin/fetch-crl -q -r 360" > /etc/cron.d/fetch-crl-docker

ADD rucio.conf.j2 /tmp/
ADD gacl /opt/rucio/etc

ENTRYPOINT ['start-server.sh']
