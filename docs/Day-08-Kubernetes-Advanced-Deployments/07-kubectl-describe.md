# `kubectl describe`

## Objective

Inspect the live Pod, Deployment, and Service in a form that brings configuration, status, ownership, and recent events together.

## Pod inspection

```bash
kubectl describe pod "$POD_NAME" -n arun-devops
```

Important observations from `arun-flask-deployment-6d8c958999-bb78m`:

| Field | Observed value | Meaning |
|---|---|---|
| Node | `desktop-control-plane/172.19.0.4` | Node selected for the Pod |
| Pod IP | `10.244.0.19` | Address inside the cluster network |
| Controlled By | `ReplicaSet/arun-flask-deployment-6d8c958999` | Immediate owner |
| Image | `arun-jenkins-flask-app:v1` | Image restored after rollback |
| State / Ready | `Running` / `True` | Container is running and ready |
| Restart Count | `0` | No container restart had occurred |
| Environment | ConfigMap and Secret key references | Values were wired from external objects |
| Conditions | all `True` | Scheduled, initialized, started, and ready |
| QoS Class | `BestEffort` | No CPU/memory requests or limits configured |
| Events | `<none>` | No retained warning/normal events to report |

`Events: <none>` does not prove that an application is correct; it means no events were retained for that object at that time. Application logs and health checks are still required.

## Deployment inspection

```bash
kubectl describe deployment arun-flask-deployment \
  -n arun-devops
```

Observed:

```text
Replicas:               2 desired | 2 updated | 2 total | 2 available | 0 unavailable
StrategyType:           RollingUpdate
RollingUpdateStrategy:  25% max unavailable, 25% max surge
Available:              True    MinimumReplicasAvailable
Progressing:            True    NewReplicaSetAvailable
NewReplicaSet:          arun-flask-deployment-6d8c958999 (2/2 replicas created)
Events:                 <none>
```

This view explained both the rollout strategy and the chain of old ReplicaSets. It also made the replica count authoritative: the live Deployment wanted two Pods.

## Service inspection

```bash
kubectl describe service arun-flask-service \
  -n arun-devops
```

Observed:

```text
Selector:    app=arun-flask
Type:        NodePort
IP:          10.96.128.221
Port:        80/TCP
TargetPort:  5000/TCP
NodePort:    32075/TCP
Endpoints:   10.244.0.18:5000,10.244.0.19:5000
Events:      <none>
```

The two endpoints were the strongest quick confirmation that the Service selector matched both Ready Pods. If this field had been empty, the next checks would be Pod labels, readiness, Service selector, port mapping, and EndpointSlice objects.

## Troubleshooting order

For an unavailable application, a practical sequence is:

1. `kubectl get pods` for broad state.
2. `kubectl describe pod` for conditions, container state, and events.
3. `kubectl logs` (and `--previous`) for application failure details.
4. `kubectl describe deployment` for desired replicas, rollout conditions, and ReplicaSets.
5. `kubectl describe service` for selectors and endpoints.
6. Test the application from the correct network path.

`describe` is valuable because it shows interpreted status and events. Use `kubectl get ... -o yaml` when the complete API object, exact fields, or managed state is needed.

