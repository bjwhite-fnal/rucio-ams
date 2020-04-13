# Fermilab Rucio Server Docker Image Specification
# 
# Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020

ARG rucio_version
FROM rucio/rucio-server:release-${rucio_version}

RUN yum install -y mod_ssl
RUN yum install -y gridsite
RUN yum install -y patch

RUN mv /etc/httpd/conf.d/zgridsite.conf /etc/httpd/conf.d/zgridsite.conf-hide

ADD oic.rpm /tmp
ADD httpd.conf /etc/httpd/conf/
ADD alembic.ini.j2 /tmp
ADD rucio.conf.j2 /tmp/
ADD rucio.cfg.j2 /tmp/
ADD fnal_rucio.conf.j2 /tmp/
ADD gacl /opt/rucio/etc/
ADD start-server.sh /

RUN rpm -i /tmp/oic.rpm; \
    echo "/usr/lib/oracle/12.2/client64/lib" >/etc/ld.so.conf.d/oracle.conf; \
    ldconfig

# Patches
ADD patches/* /tmp/patches/
RUN if ls -1 /tmp/patches/ | grep -Eq '\.patch$'; then for p in /tmp/patches/*.patch; do echo "Patching: $p" && patch -p0 -d /usr/lib/python2.7/site-packages/ < $p; done; fi

VOLUME /etc/grid-security

ENTRYPOINT ["/start-server.sh"]
