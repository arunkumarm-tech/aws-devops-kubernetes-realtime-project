# Rolling Updates

## Objective

Release `arun-jenkins-flask-app:v2` through the existing Deployment, observe Kubernetes replace the Pods, and verify that the rollout completes without intentionally stopping the application.

## Starting point

The Deployment was running image `v1`. A local `v2` tag was created from the same image ID for the mechanics exercise:

```bash
docker tag arun-jenkins-flask-app:v1 arun-jenkins-flask-app:v2
docker images | grep arun-jenkins-flask-app
```

Both tags showed image ID `b078bb59d51d`. That matters: the Kubernetes Pod template changed because the tag changed, but this did not prove that application code changed. In a real release, `v2` should point to a separately built, tested image and preferably be pinned by digest.

## Update performed

```bash
kubectl set image deployment/arun-flask-deployment \
  arun-flask-container=arun-jenkins-flask-app:v2 \
  -n arun-devops

kubectl rollout status deployment/arun-flask-deployment \
  -n arun-devops
```

Observed result:

```text
deployment.apps/arun-flask-deployment image updated
deployment "arun-flask-deployment" successfully rolled out
```

The image and history were checked with:

```bash
kubectl get deployment arun-flask-deployment \
  -n arun-devops \
  -o=jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

kubectl rollout history deployment/arun-flask-deployment \
  -n arun-devops

kubectl get pods -n arun-devops
```

The Deployment reported `arun-jenkins-flask-app:v2`, revisions 1 and 2, and three ready Pods under ReplicaSet hash `5875584d87`.

## What Kubernetes did

`kubectl set image` changed the Deployment's Pod template. A Deployment does not edit running Pods in place. Its controller created a new ReplicaSet for the new template, increased the new ReplicaSet, and reduced the old one while preserving the configured availability limits.

```text
Deployment template: v1             Deployment template: v2
        |                                     |
        v                                     v
Old ReplicaSet -------- scale down     New ReplicaSet -------- scale up
        |                                     |
      v1 Pods                               v2 Pods
```

Later, `kubectl describe deployment` showed the default strategy:

```text
StrategyType:           RollingUpdate
RollingUpdateStrategy:  25% max unavailable, 25% max surge
```

For a small replica count, Kubernetes rounds percentages when calculating whole Pods. The controller continuously reconciles toward the new desired state; `kubectl rollout status` waits for that process and reports failure if the progress deadline is exceeded.

## Verification checklist

- The image field reports `v2`.
- `kubectl rollout status` completes successfully.
- All desired Pods are Ready.
- A new ReplicaSet hash appears.
- Service endpoints continue to point to Ready Pods.
- Application and health requests return successful responses.

## Production use

A production pipeline should build one immutable artifact, scan it, push it under an unambiguous tag or digest, update the declarative manifest, and observe both Kubernetes health and application metrics. A successful Kubernetes rollout only proves that Kubernetes reached its desired state; it does not by itself prove that business behavior is correct.

For a safer release, this Deployment still needs readiness and liveness probes, CPU/memory requests and limits, a production WSGI server, and a meaningful `kubernetes.io/change-cause` or Git-based audit trail.

## Practical learning

The key observation was that a Deployment rollout is a Pod-template transition managed through ReplicaSets. Pods are replaced; they are not upgraded in place. Also, changing an image tag is not the same as shipping changed application content—our `v1` and `v2` tags shared the same local image ID.

