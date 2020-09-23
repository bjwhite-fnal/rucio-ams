#!/bin/bash

# Start Logstash for processing of events and then subsequent delivery to Elasticsearch via Kafka
envsubst < /usr/share/logstash/pipeline/logstash.conf > /usr/share/logstash/pipeline/logstash.conf

logstash --node.name rucio-${EXPERIMENT}-logstash
