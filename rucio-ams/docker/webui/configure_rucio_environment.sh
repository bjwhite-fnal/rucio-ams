#!/bin/bash
# This sets up the environment variables that are needed for the WebUI to communicate with the
#   rucio server and rucio authentication server.

# Get the IP addresses of the server and auth-server
proxy_host_var=${EXPERIMENT}-rucio.okd.fnal.gov
#proxy_host_var=${RUCIO_INT_RUCIO_SERVER_PORT_443_TCP_ADDR}
#auth_proxy_host_var=${RUCIO_INT_RUCIO_SERVER_AUTH_PORT_443_TCP_ADDR}

# Get the port that those servers are listening on
proxy_port_var=RUCIO_${EXPERIMENT^^}_RUCIO_SERVER_SERVICE_PORT
auth_proxy_port_var=RUCIO_${EXPERIMENT^^}_RUCIO_SERVER_AUTH_SERVICE_PORT

# create a command to dynamically create the proxy addresses at runtime
export_rucio_proxy_cmd=$(echo "export RUCIO_PROXY=${proxy_host_var}:\$${proxy_port_var}")

export_rucio_auth_proxy_cmd=$(echo "export RUCIO_AUTH_PROXY=auth-${proxy_host_var}:\$${auth_proxy_port_var}")
#export_rucio_auth_proxy_cmd=$(echo "export RUCIO_AUTH_PROXY=${auth_proxy_host_var}:\$${auth_proxy_port_var}")

echo "PROXY CMD: ${export_rucio_proxy_cmd}"
echo "AUTH PROXY CMD: ${export_rucio_auth_proxy_cmd}"

# Evaluate that command to get the final value in the appropriate environment variable
eval ${export_rucio_proxy_cmd}
eval ${export_rucio_auth_proxy_cmd}
echo "PROXY: ${RUCIO_PROXY}"
echo "AUTH PROXY: ${RUCIO_AUTH_PROXY}"
