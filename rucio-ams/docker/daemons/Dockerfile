# Fermilab Rucio Daemons Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020

ARG rucio_version
FROM rucio/rucio-daemons:release-${rucio_version}

RUN yum install -y less \
    fts-client \
    voms-clients \
    gfal-all \
    patch \
    net-tools \
    rsync \
    telnet

RUN python3 -m pip install metacat remote-pdb

ADD vomses /etc
ADD ./start-daemon.sh /
ADD permissions/ /opt/rucio/permissions/fermilab

# Patches
#ADD patches/* /tmp/patches/
#RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

ADD ./transfer.py /usr/local/lib/python3.6/site-packages/rucio/core/transfer.py

ENTRYPOINT ["/start-daemon.sh"]

