# Dockerfile for creating a Rucio WebUI container for use with FNAL Rucio deployments

FROM rucio/rucio-ui


RUN yum install -y net-tools vim less

ADD ./rucio.cfg.j2 /tmp/
ADD ./rucio.conf.j2 /tmp/
ADD ./docker-entrypoint.sh / 
ADD ./configure_rucio_environment.sh /
