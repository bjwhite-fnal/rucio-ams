#!/bin/bash

# Start Filebeat for delivery of Rucio logs to Elasticsearch

filebeat run --path.config /etc/filebeat -c filebeat.yml
