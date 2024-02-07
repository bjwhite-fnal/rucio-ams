# Dockerfile for the FNAL Rucio statsd service that translates OKD Rucio
# stats egress from statsd -> graphite protocol for uniform Landscape ingest

FROM statsd/statsd:latest

ADD ./statsd_config.json /usr/src/app/statsd_config.json

ENTRYPOINT [  "node", "stats.js", "/usr/src/app/statsd_config.json" ]
