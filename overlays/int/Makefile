EXPERIMENT=int
SERVER_CHART_VERSION := 32.0.0
DAEMON_CHART_VERSION := 32.0.0
UI_CHART_VERSION := 32.0.0

helm:
	helm repo add rucio https://rucio.github.io/helm-charts
	helm repo update

rucio-server: helm
	helm template fnal rucio/rucio-server --version=${SERVER_CHART_VERSION} --values=rucio/values-rucio-server.yaml > rucio/helm-rucio-server.yaml

rucio-daemons: helm
	helm template fnal rucio/rucio-daemons --version=${DAEMON_CHART_VERSION} --values=rucio/values-rucio-daemons.yaml > rucio/helm-rucio-daemons.yaml

rucio-ui: helm
	helm template fnal rucio/rucio-ui --version=${UI_CHART_VERSION} --values=rucio/values-rucio-ui.yaml > rucio/helm-rucio-ui.yaml

#rucio: rucio-server rucio-daemons rucio-ui
rucio: rucio-server rucio-daemons

#package-reaper-certs:
#	rm -rf etc/.secrets/grid-certificates
#	mkdir -p etc/.secrets/grid-certificates
#	cp /etc/grid-security/certificates/*.0 etc/.secrets/grid-certificates/
#	cp /etc/grid-security/certificates/*.signing_policy etc/.secrets/grid-certificates/
#	cd etc/.secrets && tar cfz grid-certificates.tar.gz grid-certificates/
#
#store-reaper-certs: package-reaper-certs
#	base64 --wrap=0 etc/.secrets/grid-certificates.tar.gz | vault kv patch secret/rucio/${EXPERIMENT}-rucio/rucio grid-certificates.tar.gz=-

#get-secrets:
	#mkdir -p rucio/etc/.secrets
	#vault kv get --field=${EXPERIMENT}-server-hostkey secret/rucio/${EXPERIMENT}-rucio/rucio  > rucio/etc/.secrets/hostkey.pem
	#vault kv get --field=${EXPERIMENT}-server-hostcert secret/rucio/${EXPERIMENT}-rucio/rucio  > rucio/etc/.secrets/hostcert.pem
	#vault kv get --field=${EXPERIMENT}-server-cafile secret/rucio/${EXPERIMENT}-rucio/rucio  > rucio/etc/.secrets/ca.pem
	#vault kv get --field=${EXPERIMENT}-db-conn-str secret/rucio/${EXPERIMENT}-rucio/rucio  > rucio/etc/.secrets/db-conn-str.txt
	#curl https://raw.githubusercontent.com/rucio/rucio/master/etc/automatix.json > rucio/etc/.secrets/automatix.json

#clean-secrets:
#	rm -rf rucio/etc/.secrets

run-dump: 
	kubectl kustomize .

dump: get-secrets rucio run-dump clean-secrets

run-apply:  
	kubectl apply -k .

#apply: get-secrets rucio run-apply clean-secrets
apply: rucio run-apply
