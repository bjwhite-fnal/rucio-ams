#!/bin/sh

echo "$(whoami)"
echo "$(ls -l /etc/prometheus/prometheus.yml)"

sed -i "s/REPLACE_WITH_EXPERIMENT/${EXPERIMENT}/g" /etc/prometheus/prometheus.yml

#Delimit with ^ to avoid url parsing conflict with /
sed -i "s^REPLACE_WITH_LANDSCAPE_ENDPOINT^${LANDSCAPE_REMOTE_WRITE_ENDPOINT}^g" /etc/prometheus/prometheus.yml

/bin/prometheus --config.file=/etc/prometheus/prometheus.yml --storage.tsdb.path=/prometheus --web.console.libraries=/usr/share/prometheus/console_libraries --web.console.templates=/usr/share/prometheus/consoles --log.level=debug
