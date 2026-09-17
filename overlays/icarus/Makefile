EXPERIMENT=icarus
SERVER_CHART_VERSION := 41.0.1
DAEMON_CHART_VERSION := 41.0.0
UI_CHART_VERSION := 41.1.0

helm:
	helm repo add rucio https://rucio.github.io/helm-charts
	helm repo update

rucio-server: helm
	helm template fnal rucio/rucio-server --version=${SERVER_CHART_VERSION} --values=rucio/values-rucio-server.yaml > rucio/helm-rucio-server.yaml

rucio-daemons: helm
	helm template fnal rucio/rucio-daemons --version=${DAEMON_CHART_VERSION} --values=rucio/values-rucio-daemons.yaml > rucio/helm-rucio-daemons.yaml

rucio-webui: helm
	helm template fnal rucio/rucio-webui --version=${UI_CHART_VERSION} --values=rucio/values-rucio-webui.yaml > rucio/helm-rucio-webui.yaml

rucio: rucio-server rucio-daemons rucio-webui

get-secrets:
	mkdir -p .secrets
	vault kv get -field=server-cafile    okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/ca.pem
	vault kv get -field=server-hostcert okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/hostcert.pem
	vault kv get -field=server-hostkey  okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/hostkey.pem
	vault kv get -field=idpsecrets       okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/idpsecrets.json
	vault kv get -field=db-connstr       okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/db-connstr
	vault kv get -field=hermes-rabbitmq  okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/hermes-rabbitmq
	vault kv get -field=rabbitmq-definitions.json okd/okdprod1/rucio-${EXPERIMENT}/rucio > ./.secrets/rabbitmq-definitions.json

clean-secrets:
	rm -rf .secrets

run-dump: 
	kubectl kustomize .

dump: get-secrets rucio run-dump clean-secrets

run-apply:  
	kubectl apply -k .

#apply: get-secrets rucio run-apply clean-secrets
apply: rucio run-apply
