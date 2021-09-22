# Fermilab Rucio Deployment Automatic Transfer Testing Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2021

FROM rucio/rucio-clients

ADD ./run_transfer_test.sh /run_transfer_test.sh
ADD ./listen_for_event.py /listen_for_event.py
ADD ./rucio.cfg /opt/rucio/etc

ENTRYPOINT ["/run_transfer_test.sh"]
