# Rollback

## Objective

Reverse the `v2` Deployment rollout, confirm that Kubernetes restored the earlier Pod template, and understand what a rollback does—and does not—restore.

## Commands and observed result

Before the rollback, history and the current image showed:

```text
REVISION  CHANGE-CAUSE
1         <none>
2         <none>

arun-jenkins-flask-app:v2
```

The rollback was executed with:

```bash
kubectl rollout undo deployment/arun-flask-deployment \
  -n arun-devops

kubectl rollout status deployment/arun-flask-deployment \
  -n arun-devops
```

Observed output:

```text
deployment.apps/arun-flask-deployment rolled back
deployment "arun-flask-deployment" successfully rolled out
```

Verification:

```bash
kubectl get deployment arun-flask-deployment \
  -n arun-devops \
  -o=jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'

kubectl rollout history deployment/arun-flask-deployment \
  -n arun-devops

kubectl get pods -n arun-devops
```

The image returned to:

```text
arun-jenkins-flask-app:v1
```

History then showed revisions 2 and 3. Kubernetes reuses the earlier Pod template as a new active revision; it does not rewind a numeric counter.

## ReplicaSet behavior

After the rollback, Pods again used ReplicaSet hash `7b48b8c87b`. Later ConfigMap and Secret references changed the Pod template again, producing additional ReplicaSets. The final Deployment description listed several inactive ReplicaSets and one active ReplicaSet:

```text
OldReplicaSets: arun-flask-deployment-7b48b8c87b (0/0)
                arun-flask-deployment-5875584d87 (0/0)
                arun-flask-deployment-594ff8b65f (0/0)
NewReplicaSet:  arun-flask-deployment-6d8c958999 (2/2)
```

This is expected. A Deployment retains old ReplicaSets, scaled to zero, so their Pod templates can support rollout history and undo operations. Retention is limited by `revisionHistoryLimit`.

## Why three Pods later became two

On Day 7, the Deployment was scaled imperatively to three replicas:

```bash
kubectl scale deployment arun-flask-deployment --replicas=3 -n arun-devops
```

The manifest still declared:

```yaml
spec:
  replicas: 2
```

When the manifest was applied during the ConfigMap/Secret work, Kubernetes reconciled the Deployment back to two. The rollback did not unexpectedly remove a Pod; applying the declarative file restored the replica count recorded in source.

## Production considerations

Rollback is useful when a release produces unhealthy Pods or application regressions, but it is not a database rollback and cannot reverse external side effects. Schema migrations, messages already published, and changed external state need their own backward-compatible plan.

Revision `CHANGE-CAUSE` was `<none>` in this exercise. In a team environment, connect releases to a commit SHA, pipeline run, change ticket, and image digest. Prefer GitOps reversal through source control so the live correction and declared configuration do not drift apart.

To target a specific known revision:

```bash
kubectl rollout undo deployment/arun-flask-deployment \
  --to-revision=<revision> \
  -n arun-devops
```

Always follow an undo with rollout status, Pod readiness, events, application health checks, and monitoring.

