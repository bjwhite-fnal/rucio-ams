# Copyright European Organization for Nuclear Research (CERN) 2017
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Authors:
# - Cedric Serfon, <cedric.serfon@cern.ch>, 2017
# - Thomas Beermann, <thomas.beermann@cern.ch>, 2018

FROM rucio-daemons-base

RUN yum install -y less fts-client voms-clients gfal2-python gfal-all

ADD crontab /etc
ADD vomses /etc
ADD delegate_fts_proxy.sh /
ADD start-daemon.sh /
CMD chmod +x /delegate_fts_proxy.sh

ENTRYPOINT ["/start-daemon.sh"]

