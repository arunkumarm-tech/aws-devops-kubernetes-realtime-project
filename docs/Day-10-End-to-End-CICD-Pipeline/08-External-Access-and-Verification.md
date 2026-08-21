# 08 — External Access and Verification

## Create and inspect the Service

The fresh cluster had no Service:

```bash
kubectl get service -n arun-devops
kubectl apply -f kubernetes/flask-service.yaml
kubectl get service arun-flask-service -n arun-devops -o wide
```

Observed mapping:

```text
ClusterIP: 10.100.220.82
Service port: 80
NodePort: 30094/TCP
Selector: app=arun-flask
```

Traffic path:

```text
node public IP:30094 → NodePort → Service port 80 → targetPort 5000 → Flask pod
```

The backends were checked with:

```bash
kubectl get endpoints arun-flask-service -n arun-devops
```

Actual endpoints were `192.168.28.16:5000` and `192.168.34.205:5000`. Kubernetes also warned that legacy `v1 Endpoints` was deprecated in favor of EndpointSlice; it was a warning, not a routing failure.

## Diagnose the external timeout

The first external request hung:

```bash
curl http://3.88.183.117:30094
```

The node's security group was discovered and inspected:

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters "Name=ip-address,Values=3.88.183.117" \
  --query 'Reservations[].Instances[].SecurityGroups' \
  --output table

aws ec2 describe-security-groups \
  --group-ids sg-07b4507513a2dc7b8 \
  --region us-east-1 \
  --query 'SecurityGroups[0].IpPermissions' \
  --output json
```

Port `30094` was absent. For this short-lived lab only, it was opened publicly:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id sg-07b4507513a2dc7b8 \
  --protocol tcp \
  --port 30094 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

AWS returned `"Return": true` and rule `sgr-0bda5b68bbadc73c7`.

## Final proof

```bash
curl http://3.88.183.117:30094
curl http://3.88.183.117:30094/health
```

Actual application response:

```json
{"hostname":"arun-flask-deployment-75984dfd6d-j52ch","message":"Welcome to Arun's AWS DevOps Kubernetes Real-Time Project","status":"Application running successfully"}
```

Actual health response:

```json
{"status":"healthy"}
```

The pod hostname proved the response came from EKS rather than the local container.

## Jenkins post-deployment verification

Build 13 made verification part of the pipeline:

```bash
kubectl get deployment arun-flask-deployment -n arun-devops
kubectl get pods -n arun-devops -o wide
kubectl get service arun-flask-service -n arun-devops
```

It showed `2/2` available replicas, two new running pods, and Service `80:30094/TCP`, then finished `SUCCESS`.
