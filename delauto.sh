oc delete cronjob rucio-int-autotransfer
/nashome/b/bjwhite/dev/rucio/rucio-fnal/rucio-fnal/helm/helm_scripts/gen-autotransfer.sh
/nashome/b/bjwhite/dev/rucio/rucio-fnal/rucio-fnal/helm/helm_scripts/create-autotransfer.sh
kubectl create job --from=cronjob/rucio-int-autotransfer bjwhite-test-autotransfer-1
oc get pods | grep auto
