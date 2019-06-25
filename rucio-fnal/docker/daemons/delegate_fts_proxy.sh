#!/bin/bash

export TZ=US/Central

date

log="/var/log/rucio/delegate.log"
service="https://fts3-public.cern.ch:8446"
secrets_dir="/opt/rucio/fts_secrets"

if [ ! -d $secrets_dir ]; then
	exit 0				# no need to do this ?
fi


(
	echo ====================================================================================== 
	echo $0 started at `date` 

	cd /tmp
	cp ${secrets_dir}/fts_usercert.pem ${secrets_dir}/fts_userkey.pem .
	chmod go-rwx fts_usercert.pem fts_userkey.pem
	
	echo ----voms-proxy-init----

	voms-proxy-init \
		-rfc \
		-voms dune:/dune/Role=Production \
		-cert fts_usercert.pem \
		-key fts_userkey.pem \
		-out fts_proxy.pem

	# the web server needs to be able to read this too.
	setfacl -m u:apache:r fts_proxy.pem

	echo
	echo ----fts-delegation-init----

	fts-delegation-init -v \
		-s $service \
		--proxy fts_proxy.pem
) >> $log 2>&1

echo >> $log
echo >> $log


