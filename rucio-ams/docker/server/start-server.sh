#!/bin/bash -e

if [ ! -z "$POLICY_PKG_DIR" ]; then
    if [ ! -d "$POLICY_PKG_DIR" ]; then
        echo "The value provided in POLICY_PKG_DIR does not correspond to an existant directory."
        exit 1
    fi
    export PYTHONPATH=${POLICY_PKG_DIR}:${PYTHONPATH:+:}${PYTHONPATH}
    echo "Python search path: $PYTHONPATH"
fi

j2 /tmp/00-mpm.conf.j2 > /etc/httpd/conf.modules.d/00-mpm.conf

echo "=================== /etc/httpd/conf.modules.d/00-mpm.conf ========================"
cat /etc/httpd/conf.modules.d/00-mpm.conf
echo ""

j2 /tmp/httpd.conf.j2 | sed '/^\s*$/d' > /etc/httpd/conf/httpd.conf

echo "=================== /etc/httpd/conf/httpd.conf ========================"
cat /etc/httpd/conf/httpd.conf
echo ""

if [ -f /opt/rucio/etc/rucio.cfg ]; then
    echo "rucio.cfg already mounted."
else
    echo "rucio.cfg not found. will generate one."
    python3 /usr/local/rucio/tools/merge_rucio_configs.py \
        -s /tmp/rucio.config.default.cfg $RUCIO_OVERRIDE_CONFIGS \
        --use-env \
        -d /opt/rucio/etc/rucio.cfg
fi

if [ ! -z "$RUCIO_PRINT_CFG" ]; then
    echo "=================== /opt/rucio/etc/rucio.cfg ============================"
    cat /opt/rucio/etc/rucio.cfg
    echo ""
fi

j2 /tmp/rucio.conf.j2 | sed '/^\s*$/d' > /etc/httpd/conf.d/rucio.conf

/usr/bin/memcached -u memcached -p 11211 -m 128 -c 1024 &

if [ ! -z "$RUCIO_METRICS_PORT" -a -z "$prometheus_multiproc_dir" ]; then
    echo "Setting default prometheus_multiproc_dir to /tmp/prometheus"
    export prometheus_multiproc_dir=/tmp/prometheus
fi

if [ ! -z "$RUCIO_HTTPD_LOG_DIR" ]; then
    echo "Configuring custom HTTP logging..."
    /configure_server_log_location.sh
else
    echo "Using default logging..."
fi

echo "=================== /etc/httpd/conf.d/rucio.conf ========================"
cat /etc/httpd/conf.d/rucio.conf
echo ""

j2 /tmp/alembic.ini.j2 | sed '/^\s*$/d' > /opt/rucio/etc/alembic.ini

echo "=================== /opt/rucio/etc/alembic.ini ========================"
cat /opt/rucio/etc/alembic.ini
echo ""

exec httpd -D FOREGROUND
