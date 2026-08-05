# Tips and Best Practices

## Keep declared and live state aligned

- Change manifests through source control and review the diff before applying.
- Treat imperative commands such as `kubectl scale` and `kubectl set image` as useful operational tools, but write intentional long-lived changes back to Git.
- Use `kubectl diff` and server-side dry-run in CI before deployment.
- Record the commit SHA, image digest, pipeline run, and change owner for each release.

## Make rollouts meaningful

- Build `v2` from changed, tested source; do not only add another tag to the same image.
- Prefer immutable image tags and deploy by digest where practical.
- Add readiness, liveness, and startup probes that reflect real application behavior.
- Set an appropriate progress deadline and rollout strategy for the replica count and availability target.
- Verify service behavior and metrics after Kubernetes says the rollout succeeded.
- Design database changes for backward compatibility and independent recovery.

## Manage configuration deliberately

- Use ConfigMaps only for non-sensitive configuration.
- Document required keys and fail clearly when they are absent.
- Remember that ConfigMap-backed environment variables require new Pods to change.
- Avoid large, frequently changing configuration blobs when a dedicated configuration system is more appropriate.

## Protect secrets

- Never commit live credentials, even as Base64.
- Avoid printing Secret values in terminals, screenshots, logs, or CI output.
- Rotate the credential used in this exercise if it protects any real resource.
- Limit `get/list/watch` access to Secrets and `pods/exec` through RBAC.
- Enable etcd encryption at rest and audit access.
- On AWS, use Secrets Manager or Parameter Store with an approved EKS integration and workload identity.
- Plan and test credential rotation rather than treating it as an emergency-only activity.

## Operate observable workloads

- Log structured records to stdout/stderr with timestamps, severity, request ID, and safe context.
- Centralize logs; do not depend on a particular Pod surviving.
- Do not log passwords, tokens, or full sensitive request bodies.
- Combine logs with metrics, traces, events, and health checks.
- Use `kubectl logs --previous` when a container has restarted.

## Build schedulable, resilient Pods

- Define CPU/memory requests and limits; the Day 8 Pods were `BestEffort`.
- Run as a non-root user with a read-only filesystem where the application allows it.
- Set graceful termination behavior and a suitable termination grace period.
- Spread replicas across nodes/zones in a real multi-node cluster.
- Use PodDisruptionBudgets where voluntary-disruption availability requires them.

## Troubleshoot safely

- Start with read-only evidence: `get`, `describe`, logs, events, and endpoints.
- Confirm namespace and context before changing anything.
- Check that `$POD_NAME` is populated and that the prompt shows the expected environment.
- Do not repair a running container manually. Fix the image or manifest and redeploy.
- Prefer ephemeral debug containers for minimal images, subject to team policy.
- Stop port-forward sessions when testing is complete; they are temporary local tunnels, not access architecture.

## Production changes still needed in this project

1. Reconcile the tested Day 8 environment references into the committed Deployment manifest.
2. Replace the Flask development server with a production WSGI server.
3. Add probes and resource requests/limits.
4. Publish an immutable image to ECR and reference its full URI/digest.
5. Add centralized logging and monitoring.
6. Use a managed secret workflow rather than literal CLI values.
7. Expose EKS traffic through an Ingress or load balancer with DNS and TLS.

