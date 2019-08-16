#!/bin/bash

echo "Pushing all images..."
./push-cache.sh && \
./push-messenger.sh && \
./push-daemons.sh && \
./push-server.sh
