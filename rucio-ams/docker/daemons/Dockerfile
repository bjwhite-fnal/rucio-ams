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
ADD rucio.cfg.j2 /tmp

#TEMP
#ADD reaper.py /usr/local/lib/python3.6/site-packages/rucio/daemons/reaper/reaper.py

# Patches
#ADD patches/* /tmp/patches/
#RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

ENTRYPOINT ["/start-daemon.sh"]

