oc delete deployments --all
oc delete secrets --all
oc delete route --all
oc delete services -l "app=rucio-server"
oc delete services -l "app=rucio-server-auth"
oc delete configmaps --all
oc delete ingress --all
oc delete cronjobs --all
oc delete pods --all --now

