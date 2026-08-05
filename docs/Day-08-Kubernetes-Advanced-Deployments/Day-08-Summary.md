# Day 8 Summary

## Outcome

The Flask application moved through a complete local release-and-debug cycle. We updated the Deployment from `v1` to a locally tagged `v2`, watched the rolling update finish, inspected revision history, rolled back to `v1`, and confirmed the active image. We then separated application configuration and database credentials from the image, caused new Pods to be created from that template, and verified the runtime environment.

The final checks went beyond “Pod is Running.” We inspected container logs, followed real HTTP requests, entered the container, described all three primary resources, and verified that the Service had two healthy endpoints.

## Final observed state

```text
Deployment: arun-flask-deployment
Namespace:  arun-devops
Image:      arun-jenkins-flask-app:v1
Replicas:   2 desired / 2 available
Strategy:   RollingUpdate

Active ReplicaSet: arun-flask-deployment-6d8c958999
Pods:              10.244.0.18 and 10.244.0.19

Service:    arun-flask-service
ClusterIP:  10.96.128.221
Port path:  80 -> 5000
NodePort:   32075
Endpoints:  10.244.0.18:5000, 10.244.0.19:5000
```

Pod inspection showed all conditions True, zero restarts, ConfigMap and Secret references, and no events. It also showed `BestEffort` QoS, highlighting the absence of resource requests and limits.

## Evidence captured

- Successful rollout and rollback messages.
- Revisions 1, 2, and 3 across the update/undo sequence.
- ConfigMap values `APP_ENV=development` and `APP_MESSAGE=Running from Kubernetes ConfigMap` inside the container.
- Secret key references and successful injection (values redacted here).
- Flask startup on `0.0.0.0:5000`, with loopback and Pod-IP addresses displayed.
- `GET /` and `GET /health` requests returning HTTP 200.
- `/app`, `app.py`, and `requirements.txt` visible through `kubectl exec`.
- Both Pod addresses listed as Service endpoints.

## Strongest lessons

1. A Deployment replaces Pods through ReplicaSets; it does not edit containers in place.
2. Rollback restores a Pod template, not database or other external state.
3. A live imperative scale is temporary if the manifest still declares another value.
4. Creating a ConfigMap or Secret has no application effect until the workload references it.
5. Base64 is not encryption, and printing a secret for verification creates exposure.
6. Namespace, terminal session, container context, and request-to-Pod correlation all matter during diagnosis.
7. `Running` is only one signal; readiness, endpoints, logs, HTTP behavior, and events complete the picture.

## Documentation index

- [Rolling Updates](01-Rolling-Updates.md)
- [Rollback](02-Rollback.md)
- [ConfigMaps](03-ConfigMaps.md)
- [Secrets](04-Secrets.md)
- [`kubectl logs`](05-kubectl-logs.md)
- [`kubectl exec`](06-kubectl-exec.md)
- [`kubectl describe`](07-kubectl-describe.md)
- [Commands Reference](Commands-Reference.md)
- [Interview Questions](Interview-Questions.md)
- [Troubleshooting](Troubleshooting.md)
- [Tips and Best Practices](Tips-and-Best-Practices.md)
- [Mistakes We Made](Mistakes-We-Made.md)

## Next engineering step

Before treating the repository as deployable source of truth, reconcile the ConfigMap and Secret references that were tested live into the committed Deployment manifest, without committing plaintext credentials. Then add probes, resources, a production WSGI server, and an ECR-based immutable release path for the move to EKS.

