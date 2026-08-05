# Day 8 Commands Reference

Replace angle-bracket placeholders before running a command. All project resources belong in `arun-devops`.

## Baseline

```bash
kubectl get nodes
kubectl get deployments -n arun-devops
kubectl get pods -n arun-devops -o wide
kubectl get services -n arun-devops
```

## Rolling update and rollback

```bash
docker tag arun-jenkins-flask-app:v1 arun-jenkins-flask-app:v2
docker images | grep arun-jenkins-flask-app

kubectl set image deployment/arun-flask-deployment \
  arun-flask-container=arun-jenkins-flask-app:v2 \
  -n arun-devops

kubectl rollout status deployment/arun-flask-deployment -n arun-devops
kubectl rollout history deployment/arun-flask-deployment -n arun-devops

kubectl rollout undo deployment/arun-flask-deployment -n arun-devops
kubectl rollout undo deployment/arun-flask-deployment \
  --to-revision=<revision> -n arun-devops

kubectl get deployment arun-flask-deployment \
  -n arun-devops \
  -o=jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

## ConfigMap

```bash
kubectl create configmap arun-flask-config \
  --from-literal=APP_ENV=development \
  --from-literal=APP_MESSAGE="Running from Kubernetes ConfigMap" \
  -n arun-devops

kubectl get configmap arun-flask-config -n arun-devops -o yaml
```

## Secret

```bash
kubectl create secret generic arun-flask-secret \
  --from-literal=DB_USERNAME='<username>' \
  --from-literal=DB_PASSWORD='<password>' \
  -n arun-devops

kubectl get secret arun-flask-secret -n arun-devops
kubectl describe secret arun-flask-secret -n arun-devops
```

## Apply and verify

```bash
kubectl apply --dry-run=server -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl rollout status deployment/arun-flask-deployment -n arun-devops

POD_NAME=$(kubectl get pods -n arun-devops \
  -l app=arun-flask \
  -o jsonpath='{.items[0].metadata.name}')

echo "$POD_NAME"
kubectl exec -n arun-devops "$POD_NAME" -- env | grep APP_
```

Avoid printing Secret values during normal operations. The following was used only as a controlled learning verification:

```bash
kubectl exec -n arun-devops "$POD_NAME" -- env | grep DB_
```

## Exec and describe

```bash
kubectl exec -it "$POD_NAME" -n arun-devops -- sh
pwd
ls -la
env | grep APP
exit

kubectl describe pod "$POD_NAME" -n arun-devops
kubectl describe deployment arun-flask-deployment -n arun-devops
kubectl describe service arun-flask-service -n arun-devops
```

## Logs and local test

```bash
kubectl logs -n arun-devops "$POD_NAME"
kubectl logs -f -n arun-devops "$POD_NAME"
kubectl logs --previous -n arun-devops "$POD_NAME"
kubectl logs --tail=100 --timestamps -n arun-devops "$POD_NAME"

kubectl port-forward -n arun-devops \
  service/arun-flask-service 8081:80

curl http://localhost:8081
curl http://localhost:8081/health
```

## Useful diagnosis

```bash
kubectl get replicasets -n arun-devops
kubectl get endpointslices -n arun-devops \
  -l kubernetes.io/service-name=arun-flask-service
kubectl get events -n arun-devops --sort-by=.metadata.creationTimestamp
kubectl diff -f kubernetes/flask-deployment.yaml
```

