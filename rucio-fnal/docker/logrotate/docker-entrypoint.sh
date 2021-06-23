#!/bin/bash

echo "Starting rotation of logs."
logrotate /etc/logrotate.d/logrotate.conf
echo "Rotation of logs completed with return code: ${?}"
