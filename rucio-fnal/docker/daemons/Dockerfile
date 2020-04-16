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

RUN pip install remote-pdb

ADD rucio.cfg.j2 /tmp/
ADD start-daemon.sh /
ADD crontab /etc
ADD vomses /etc
ADD delegate_fts_proxy.sh /
CMD chmod +x /delegate_fts_proxy.sh

# Patches
ADD patches/* /tmp/patches/
RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

ENTRYPOINT ["/start-daemon.sh"]

