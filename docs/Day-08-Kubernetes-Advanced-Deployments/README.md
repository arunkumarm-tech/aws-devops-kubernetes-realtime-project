# Day 8 — Kubernetes Advanced Deployments and Troubleshooting

Day 8 started with a healthy three-Pod Flask Deployment from Day 7 and moved into the work that normally happens after an application is running: releasing a new image, watching the rollout, reversing it, separating configuration from the image, injecting sensitive values, and diagnosing the live workload.

This is a record of the work performed on the local Docker Desktop Kubernetes cluster. It is intentionally specific to this project rather than a general Kubernetes tutorial.

## Environment used

| Item | Value |
|---|---|
| Cluster | Docker Desktop, single control-plane node |
| Kubernetes version observed | `v1.34.3` |
| Namespace | `arun-devops` |
| Deployment | `arun-flask-deployment` |
| Container | `arun-flask-container` |
| Service | `arun-flask-service` (`NodePort`) |
| Service routing | port `80` to container port `5000` |
| Images exercised | `arun-jenkins-flask-app:v1` and `v2` |
| ConfigMap | `arun-flask-config` |
| Secret | `arun-flask-secret` |

## What was completed

- Changed the Deployment image from `v1` to `v2` and waited for a successful rolling update.
- Inspected rollout revisions and the ReplicaSets created by Deployment template changes.
- Rolled the Deployment back and confirmed that `v1` was restored.
- Created `arun-flask-config` and injected `APP_ENV` and `APP_MESSAGE`.
- Created an Opaque Secret and injected `DB_USERNAME` and `DB_PASSWORD`.
- Verified the injected values inside a running container.
- Used `kubectl logs` and `kubectl logs -f` to inspect startup and HTTP access logs.
- Used `kubectl exec` to inspect `/app`, application files, and the container environment.
- Described the Pod, Deployment, and Service, including conditions, ReplicaSets, endpoints, and events.
- Diagnosed real errors involving YAML indentation, namespaces, shell placeholders, shell-variable scope, replica drift, and a keyboard character.

## Runtime picture at the end of the exercise

```text
curl localhost:8081
        |
        | temporary port-forward 8081 -> 80
        v
Service: arun-flask-service (10.96.128.221)
        | selector: app=arun-flask
        | targetPort: 5000
        +---------------------------+
        |                           |
        v                           v
Pod 10.244.0.18:5000       Pod 10.244.0.19:5000
Flask image v1              Flask image v1
ConfigMap + Secret env      ConfigMap + Secret env
```

The final Deployment reported `2 desired`, `2 updated`, `2 available`, and `0 unavailable`. The Service listed both Pod IPs as endpoints. The reduction from three Pods on Day 7 to two on Day 8 was not caused by rollback: the committed manifest still declared `replicas: 2`, so applying it restored the declarative value.

## Documentation map

1. [Rolling Updates](01-Rolling-Updates.md)
2. [Rollback](02-Rollback.md)
3. [ConfigMaps](03-ConfigMaps.md)
4. [Secrets](04-Secrets.md)
5. [kubectl logs](05-kubectl-logs.md)
6. [kubectl exec](06-kubectl-exec.md)
7. [kubectl describe](07-kubectl-describe.md)
8. [Commands Reference](Commands-Reference.md)
9. [Interview Questions](Interview-Questions.md)
10. [Troubleshooting](Troubleshooting.md)
11. [Tips and Best Practices](Tips-and-Best-Practices.md)
12. [Mistakes We Made](Mistakes-We-Made.md)
13. [Day 8 Summary](Day-08-Summary.md)

## Repository-state note

The Day 8 terminal session showed the ConfigMap and Secret references working in the live Deployment. At the time this documentation was prepared, the repository's committed `kubernetes/flask-deployment.yaml` still contained the original Day 7 container definition. The examples in these pages preserve the tested Day 8 configuration, but the manifest itself has not been changed as part of this documentation task.

## Production boundary

Everything here ran locally and created no AWS infrastructure. A production version would normally pull immutable images from ECR, run on EKS, expose traffic through an Ingress or load balancer, use readiness/liveness probes and resource requests, and obtain secrets from a controlled secrets system. `kubectl port-forward` and Flask's built-in development server are useful for local verification, not production serving.

