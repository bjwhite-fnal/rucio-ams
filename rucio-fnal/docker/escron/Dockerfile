# Fermilab Rucio Elasticsearch Exporter Docker Image Specification
# Originally by DUNE Data Management
#
# OKD Author:
# - Brandon White, <bjwhite@fnal.gov>, 2020

FROM rucio/rucio-clients

ADD ./from_mq_to_es.py /from_mq_to_es.py
ADD ./start-export.sh /start-export.sh


ENTRYPOINT ["/start-export.sh"]
