.venv\Scripts\activate.bat

uvicorn microservices.agent-service.app.main --reload
uvicorn microservices.sales-integration-service.app.main --reload


docker network create cmm707-microservices

docker build -t agent-service -f microservices/agent-service/Dockerfile microservices/agent-service
docker run --network cmm707-microservices -p 8000:8000 --env-file .env agent-service

docker build -t sales-integration-service -f microservices/sales-integration-service/Dockerfile microservices/sales-integration-service
docker run --network cmm707-microservices -p 8001:8001 --env-file .env sales-integration-service

docker-compose down 
docker-compose up -d --build


docker-compose logs sales-integration-service













kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/agent-service.yaml
kubectl apply -f k8s/sales-integration-service.yaml
kubectl apply -f k8s/notification-service.yaml
kubectl get pods -n cmm707-microservices
kubectl apply -f k8s/ingress.yaml
kubectl get ingress -n cmm707-microservices



agent-service-5669789b97-zfsgb               0/1     ImagePullBackOff   0          10m
notification-service-69ff985764-4hfkx        0/1     ImagePullBackOff   0          10m
sales-integration-service-767dcc49db-nq7hj   0/1     ImagePullBackOff   0          10m


kubectl logs agent-service-5669789b97-zfsgb -n cmm707-microservices




# docker-compose up -d --build

# docker-compose logs agent-service
# docker-compose logs sales-integration-service
# docker-compose logs notification-service

kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/agent-service.yaml
kubectl apply -f k8s/sales-integration-service.yaml
kubectl apply -f k8s/notification-service.yaml
kubectl get pods -n cmm707-microservices
kubectl apply -f k8s/ingress.yaml
kubectl get ingress -n cmm707-microservices


kubectl port-forward -n cmm707-microservices svc/agent-service 8000:8000
kubectl port-forward -n cmm707-microservices svc/sales-integration-service 8001:8001
kubectl port-forward -n cmm707-microservices svc/notification-service 8002:8002
<!-- kubectl port-forward -n cmm707-microservices svc/aggregator-service 8003:8003 -->


kubectl get all -n cmm707-microservices
kubectl get pods -n cmm707-microservices
kubectl get svc -n cmm707-microservices
kubectl get ingress -n cmm707-microservices


$pods = kubectl get pods -n cmm707-microservices --no-headers -o custom-columns=":metadata.name"
foreach ($pod in $pods) {
  Write-Host "`n=== Logs for $pod ==="
  kubectl logs $pod -n cmm707-microservices
}


kubectl exec -it agent-service-5669789b97-zfsgb -n cmm707-microservices -- /bin/sh




git config --global user.name "machinelearningzuu"
git config --global user.email "isurualagiyawanna9717@gmail.com"