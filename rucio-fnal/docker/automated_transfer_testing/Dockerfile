# Fermilab Rucio Deployment Automatic Transfer Testing Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2021

FROM rucio/rucio-clients

ADD ./run_transfer_test.sh /run_transfer_test.sh

ENTRYPOINT ["/run_transfer_test.sh"]
