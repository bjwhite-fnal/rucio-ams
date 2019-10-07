#!/bin/bash

proxy_host_var=${EXPERIMENT}-rucio.fnal.gov
proxy_port_var=RUCIO_${EXPERIMENT^^}_RUCIO_SERVER_SERVICE_PORT
auth_proxy_port_var=RUCIO_${EXPERIMENT^^}_RUCIO_SERVER_AUTH_SERVICE_PORT
export_rucio_proxy_cmd=$(echo "export RUCIO_PROXY=${proxy_host_var}:\$${proxy_port_var}")
export_rucio_auth_proxy_cmd=$(echo "export RUCIO_AUTH_PROXY=${proxy_host_var}:\$${auth_proxy_port_var}")
echo "PROXY CMD: ${export_rucio_proxy_cmd}"
echo "AUTH PROXY CMD: ${export_rucio_auth_proxy_cmd}"
eval ${export_rucio_proxy_cmd}
eval ${export_rucio_auth_proxy_cmd}
echo "PROXY: ${RUCIO_PROXY}"
echo "AUTH PROXY: ${RUCIO_AUTH_PROXY}"
