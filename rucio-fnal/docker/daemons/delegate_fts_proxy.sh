#!/bin/bash

export TZ=US/Central

date

log="/var/log/rucio/delegate.log"

if [[ -z $EXPERIMENT ]]; then
    echo "Please ensure that you have EXPERIMENT set to the name of your experiment."
    exit -1
fi


(
	echo ====================================================================================== 
	echo $0 started at `date` 

	cd /tmp
	cp /etc/grid-security/hostcert.pem /etc/grid-security/hostkey.pem .
	chmod go-rwx hostcert.pem hostkey.pem
	
	echo ----voms-proxy-init----

	voms-proxy-init \
		-rfc \
		-voms $EXPERIMENT:/$EXPERIMENT/Role=Production \
		-cert hostcert.pem \
		-key hostkey.pem \
		-out fts_proxy.pem

	# the web server needs to be able to read this too.
	setfacl -m u:apache:r fts_proxy.pem

	echo
	echo ----fts-delegation-init----

	fts-delegation-init -v \
		-s $RUCIO_CFG_CONVEYOR_FTSHOSTS \
		--proxy fts_proxy.pem
) >> $log 2>&1

echo >> $log
echo >> $log


