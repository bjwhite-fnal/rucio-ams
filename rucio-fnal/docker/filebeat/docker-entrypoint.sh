#!/bin/bash

# Start Filebeat for delivery of Rucio logs to Logstash 
envsubst < /usr/share/filebeat/filebeat.yml > /usr/share/filebeat/filebeat.yml

filebeat run --path.config /usr/share/filebeat -c filebeat.yml
