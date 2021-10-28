#!/bin/sh

# FNAL Specific Configuration
if [ ! -z "$POLICY_PKG_DIR" ]; then
    if [ ! -d "$POLICY_PKG_DIR" ]; then
        echo "The value provided in POLICY_PKG_DIR does not correspond to an existant directory."
        exit 1
    fi
    export PYTHONPATH=${POLICY_PKG_DIR}:${PYTHONPATH:+:}${PYTHONPATH}
    echo "Python search path: $PYTHONPATH"
fi

if [ -z "$RUCIO_DAEMON_LOG_DIR" ]; then
    echo "Make sure to set RUCIO_DAEMON_LOG_DIR!"
    exit 1
fi
# End FNAL Specific Configuration

if [ -f /opt/rucio/etc/rucio.cfg ]; then
    echo "rucio.cfg already mounted."
else
    echo "rucio.cfg not found. will generate one."
    python3 /tmp/merge_rucio_configs.py \
        -s /tmp/rucio.config.default.cfg $RUCIO_OVERRIDE_CONFIGS \
        --use-env \
        -d /opt/rucio/etc/rucio.cfg
fi

if [ ! -z "$RUCIO_PRINT_CFG" ]; then
    echo "=================== /opt/rucio/etc/rucio.cfg ============================"
    cat /opt/rucio/etc/rucio.cfg
    echo ""
fi

/usr/bin/memcached -u memcached -p 11211 -m 64 -c 1024 &

if [ "$RUCIO_DAEMON" == "hermes" ]
then
  echo "starting sendmail for $RUCIO_DAEMON"
  sendmail -bd
fi

if [ -d "/patch" ]
then
    echo "Patches found. Trying to apply them"
    for patchfile in /patch/*
    do
        echo "Apply patch ${patchfile}"
        patch -p3 -d /usr/local/lib/python3.6/site-packages/rucio < $patchfile
    done
fi

echo "starting daemon with: $RUCIO_DAEMON $RUCIO_DAEMON_ARGS"
echo ""

if [ -z "$RUCIO_ENABLE_LOGS" ]; then
    eval "/usr/bin/python3 /usr/local/bin/rucio-$RUCIO_DAEMON $RUCIO_DAEMON_ARGS"
else
    eval "/usr/bin/python3 /usr/local/bin/rucio-$RUCIO_DAEMON $RUCIO_DAEMON_ARGS \
        >> ${RUCIO_DAEMON_LOG_DIR}/${RUCIO_DAEMON}.log 2>> ${RUCIO_DAEMON_LOG_DIR}/${RUCIO_DAEMON}.error.log"
fi
