#!/bin/bash -e

if [ ! -z "$POLICY_PKG_DIR" ]; then
    if [ ! -d "$POLICY_PKG_DIR" ]; then
        echo "The value provided in POLICY_PKG_DIR does not correspond to an existant directory."
        exit 1
    fi
    export PYTHONPATH=$POLICY_PKG_DIR:$PYTHONPATH
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
    j2 /tmp/rucio.cfg.j2 | sed '/^\s*$/d' > /opt/rucio/etc/rucio.cfg
fi

if [ ! -z "$RUCIO_PRINT_CFG" ]; then
    echo "=================== /opt/rucio/etc/rucio.cfg ============================"
    cat /opt/rucio/etc/rucio.cfg
    echo ""
fi

j2 /tmp/rucio.conf.j2 | sed '/^\s*$/d' > /etc/httpd/conf.d/rucio.conf

if [ ! -z "$RUCIO_HTTPD_LOG_DIR" ]; then
    /configure_server_log_location.sh
fi

echo "=================== /etc/httpd/conf.d/rucio.conf ========================"
cat /etc/httpd/conf.d/rucio.conf
echo ""

j2 /tmp/alembic.ini.j2 | sed '/^\s*$/d' > /opt/rucio/etc/alembic.ini

echo "=================== /opt/rucio/etc/alembic.ini ========================"
cat /opt/rucio/etc/alembic.ini
echo ""

httpd -D FOREGROUND
