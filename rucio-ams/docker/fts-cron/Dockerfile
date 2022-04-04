# Fermilab fts-cron Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020

FROM rucio/fts-cron:latest

# Add the FNAL specific VOMS servers
RUN rm /etc/vomses/*
ADD ./vomses /etc/vomses/

RUN mkdir -p -m 775 /opt/rucio/fts-delegate/

ADD docker-entrypoint.sh /opt/rucio/fts-delegate/
ADD renew_fts_proxy.sh.j2 /opt/rucio/fts-delegate/
ADD renew_fts_proxy_atlas.sh.j2 /opt/rucio/fts-delegate/
ADD renew_fts_proxy_dteam.sh.j2 /opt/rucio/fts-delegate/
ADD renew_fts_proxy_tutorial.sh.j2 /opt/rucio/fts-delegate/

ADD ./docker-entrypoint.sh /
