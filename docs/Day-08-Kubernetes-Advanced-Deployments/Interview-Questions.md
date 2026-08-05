# Day 8 Interview Questions

These answers are phrased around the project that was actually performed.

## Rolling updates

### 1. What triggers a Deployment rollout?

A change to `spec.template`, such as the container image or environment references. Changing only Deployment metadata does not create new Pods.

### 2. What happened when the image changed from `v1` to `v2`?

The Deployment controller created a new ReplicaSet for the new Pod template, scaled it up, and scaled the previous ReplicaSet down.

### 3. Were `v1` and `v2` different application builds here?

No. Both tags had the same image ID. The exercise proved rollout mechanics, not an application-code change.

### 4. What does `kubectl rollout status` prove?

It proves Kubernetes completed or failed the rollout against its readiness/progress rules. It does not prove every business function is correct.

### 5. What were the Deployment's update limits?

The description showed `25% max unavailable` and `25% max surge`.

### 6. Why use readiness probes during a rolling update?

They prevent a Service from sending traffic to a new Pod until the application is actually ready.

### 7. Why prefer immutable tags or digests?

They make a release reproducible and prevent a mutable tag from referring to different bytes later.

## Rollback and ReplicaSets

### 8. What did `kubectl rollout undo` restore?

It restored the previous Deployment Pod template, which returned the image to `v1`.

### 9. Why did history show a new revision after undo?

A rollback promotes an earlier template as a new current revision; revision numbers continue forward.

### 10. Why were old ReplicaSets still visible?

Deployments retain old ReplicaSets, usually at zero replicas, to support history and rollback.

### 11. Can a Deployment rollback reverse a database migration?

No. External state and schema changes need a separate backward-compatible migration and recovery plan.

### 12. Why did the replicas fall from three to two?

Day 7 used an imperative scale to three, while the manifest still declared two. Applying the manifest reconciled the live Deployment back to two.

### 13. How would you roll back to a specific revision?

Use `kubectl rollout undo deployment/<name> --to-revision=<n> -n <namespace>` and then verify the rollout and application.

### 14. What was missing from `CHANGE-CAUSE`?

Every revision showed `<none>`. A production release should be traceable to a commit, pipeline, ticket, and image digest.

## ConfigMaps

### 15. Why was a ConfigMap used?

To separate `APP_ENV` and `APP_MESSAGE` from the image so environment-specific configuration could change independently.

### 16. Did creating the ConfigMap update the Pods?

No. The Deployment first had to reference its keys, and new Pods had to be created.

### 17. How were the values verified?

By executing `env | grep APP_` in a running Pod and observing both expected variables.

### 18. Why did the first ConfigMap Deployment apply fail?

The `env` list was indented outside the container item, so the generated object had an invalid schema.

### 19. Do ConfigMap-backed environment variables update live?

No. Environment values are fixed at container start; Pods must be replaced to receive changes.

### 20. When would you mount a ConfigMap as files?

When the application consumes configuration files and can reload them, rather than only reading process environment at startup.

## Secrets

### 21. Does Kubernetes generate the database password?

Not in this workflow. Kubernetes stored the value supplied to `kubectl create secret`.

### 22. Are Secret values encrypted because they appear as Base64?

No. Base64 is reversible encoding. Encryption at rest and strict RBAC are separate controls.

### 23. Why did namespace matter?

The Pod and Secret must be in the same namespace for a normal Secret reference. Omitting `-n arun-devops` created a different object in the default namespace.

### 24. How were Secret values injected?

Each environment variable used `valueFrom.secretKeyRef` with the Secret name and key.

### 25. Why avoid verifying secrets with `env` in production?

It exposes plaintext in the terminal, shell history, recordings, or support logs. The exercise used it only to prove injection.

### 26. How would this change on EKS?

Use controlled secret storage such as AWS Secrets Manager and an approved synchronization or CSI integration, together with IAM and Kubernetes RBAC.

### 27. What should happen to the demonstrated password?

It should not be reused; if it protects anything real, rotate it because it appeared in terminal output.

## Logs

### 28. What is the difference between `kubectl logs` and `kubectl logs -f`?

The first reads available output and exits; `-f` continues following new output.

### 29. What did the HTTP log lines prove?

`GET /` and `GET /health` returned status 200 from the selected Flask Pod.

### 30. Why did Flask print both localhost and a Pod IP?

It listened on all interfaces. Flask displayed loopback and the Pod-network address for the same server.

### 31. Why was `$POD_NAME` empty in another terminal?

Shell variables belong to the process/session where they were set unless deliberately exported and inherited.

### 32. What does `--previous` do?

It retrieves logs from the previous terminated instance of a container in the same Pod, useful after a restart.

### 33. Why is `kubectl logs` insufficient for production observability?

Pods are ephemeral and incidents span replicas. Centralized structured logging provides retention, search, correlation, and access control.

## Exec

### 34. What does `kubectl exec -it` do?

It runs a command in a container with stdin open and a pseudo-terminal allocated.

### 35. What does `--` mean in an exec command?

It separates kubectl's arguments from the command and arguments to run inside the container.

### 36. How did we prove we were inside the container?

`pwd` returned `/app`, and `ls` showed `app.py` and `requirements.txt` rather than the Mac project tree.

### 37. Why did `<pod-name>` fail when typed literally?

It was placeholder notation, and zsh interpreted angle brackets as redirection syntax.

### 38. Why might `sh`, `ping`, or `nslookup` be unavailable?

Minimal/distroless images intentionally omit shells and diagnostic utilities to reduce size and attack surface.

### 39. Should engineers repair a Pod through exec?

No. Diagnose through exec when approved, then fix the image or manifest and redeploy so the correction is repeatable.

## Describe and networking

### 40. What did `Controlled By` show?

The Pod was owned by ReplicaSet `arun-flask-deployment-6d8c958999`, which was managed by the Deployment.

### 41. What did `QoS Class: BestEffort` reveal?

No CPU or memory requests/limits were configured, making the Pods first candidates for eviction under node pressure.

### 42. What did `Events: <none>` mean?

No events were retained for that object at inspection time; it did not replace application health validation.

### 43. How did the Service choose Pods?

Its selector `app=arun-flask` matched the label on the Deployment's Pods.

### 44. What was the traffic port mapping?

Service port 80 forwarded to target port 5000 on the selected Pod. NodePort 32075 provided a node-level entry point.

### 45. What did the endpoint list prove?

Both Ready Pods, `10.244.0.18:5000` and `10.244.0.19:5000`, were available as Service backends.

### 46. What would an empty endpoints list suggest?

A selector/label mismatch, no Ready matching Pods, the wrong namespace, or an incorrect Service definition.

### 47. Why was port-forward used?

It created a temporary local path from `localhost:8081` to Service port 80 for development testing.

### 48. Is port-forward a production ingress mechanism?

No. Production clients normally use an Ingress or external/internal load balancer with DNS and TLS.

### 49. What is the difference between Service ClusterIP and Pod IP?

The Service IP is stable for the Service's lifetime; Pod IPs belong to replaceable Pods and can change.

### 50. What is the first useful troubleshooting sequence for this workload?

Check Pods, describe the failing Pod, inspect current/previous logs, describe the Deployment, inspect Service endpoints, then test the request path.

