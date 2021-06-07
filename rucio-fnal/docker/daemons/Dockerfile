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
    telnet

RUN python3 -m pip install remote-pdb

ADD vomses /etc
ADD ./start-daemon.sh /
ADD permissions/ /opt/rucio/permissions/fermilab

# TEMPORARY CONFIG ADD FOR UNTIL THE STUFF GETS BUILT INTO THE REAL CONTAINERS 
# TODO: THIS IS FOR:
# THIS BREAKS:
ADD rucio.cfg.j2 /tmp

# Patches
#ADD patches/* /tmp/patches/
#RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

ENTRYPOINT ["/start-daemon.sh"]

