#!/bin/bash

# This script will look at the name of the container that it is running in,
#   and then, if RUCIO_HTTPD_LOG_DIR is enabled, set the CustomLog and ErrorLog directives
#   in `/etc/httpd/conf.d/rucio.conf`
#   The point of this is to make sure that the server/auth-server logs each go to their own file, rather than a combined file.

host_name=`hostname`

echo $host_name

if [[ "$host_name" == *"auth"* ]]; then
    name_prefix="auth_"
else
    name_prefix=""
fi

echo $name_prefix

# TODO: Figure out the capture groups to grab the custom path at the front while still being able to add the prefix we need to the filename that is put back into the modified rucio.conf file.
sed -e "s% CustomLog \([/A-Za-z_-]*\)/access_log% CustomLog \1/${name_prefix}access_log%g" /etc/httpd/conf.d/rucio.conf > /etc/httpd/conf.d/rucio.conf.sed
sed -e "s% ErrorLog \([/A-Za-z_-]*\)/error_log% ErrorLog \1/${name_prefix}error_log%g" /etc/httpd/conf.d/rucio.conf.sed > /etc/httpd/conf.d/rucio.conf
