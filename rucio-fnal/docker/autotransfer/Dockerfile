# Fermilab Rucio Deployment Automatic Transfer Testing Docker Image Specification
#
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2021-2049

ARG rucio_version
FROM rucio/rucio-clients:release-${rucio_version}

ADD ./run_test.sh /run_test.sh
ADD ./run_transfer_test.py /run_transfer_test.py
ADD ./rucio.cfg /opt/rucio/etc/rucio.cfg
#TMP
#ADD ./gfal.py /usr/local/lib/python3.6/site-packages/rucio/rse/protocols/gfal.py

RUN pip3 install stomp.py remote-pdb

USER root
# Install the OSG repos
RUN yum install -y yum-plugin-priorities
RUN yum install -y https://repo.opensciencegrid.org/osg/3.4/osg-3.4-el7-release-latest.rpm
# Install the OSG CA certificates
RUN yum install -y osg-ca-certs vo-client
RUN yum install -y strace telnet net-tools
RUN yum clean all
#USER 1000

ENTRYPOINT ["/run_test.sh"]
