
kubectl apply -f rbac.yml
kubectl apply -f elasticsearch.yaml
kubectl apply -f logstash.yaml
kubectl apply -f filebeats.yaml
kubectl apply -f kibana.yaml

#kubectl port-forward -n kube-system svc/elasticsearch-logging 9200:9200
