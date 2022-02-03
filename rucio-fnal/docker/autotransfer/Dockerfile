# Fermilab Rucio Deployment Automatic Transfer Testing Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2021-2049

FROM rucio/rucio-clients

ADD ./run_test.sh /run_test.sh
ADD ./run_transfer_test.py /run_transfer_test.py
ADD ./rucio.cfg /opt/rucio/etc/rucio.cfg
RUN pip3 install stomp.py remote-pdb

USER root
RUN yum install -y telnet
ADD ./x509up_u51660 /opt/rucio/etc/proxy
RUN chown 1000 /opt/rucio/etc/proxy
USER 1000

ENTRYPOINT ["/run_test.sh"]
