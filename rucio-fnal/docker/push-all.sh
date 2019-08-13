#!/bin/bash

echo "Pushing all images..."
./push-cache.sh && \
./push-daemons.sh && \
./push-server.sh
