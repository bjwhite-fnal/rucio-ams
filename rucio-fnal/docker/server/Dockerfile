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

RUN mv /etc/httpd/conf.d/zgridsite.conf /etc/httpd/conf.d/zgridsite.conf-hide

ADD rucio.conf.j2 /tmp/
ADD gacl /opt/rucio/etc
ADD start-server.sh /

ENTRYPOINT ["/start-server.sh"]
