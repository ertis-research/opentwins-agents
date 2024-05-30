@ECHO OFF
kubectl create token ot-agents -n digitaltwins
kubectl port-forward --namespace digitaltwins svc/minio 9000:9000