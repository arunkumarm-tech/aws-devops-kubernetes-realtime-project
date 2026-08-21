# Tips and Best Practices

## Practices demonstrated

- Synchronize the local branch before starting a new day's work.
- Keep the Jenkinsfile in Git and make focused commits.
- Treat a failed stage as evidence: identify the last successful boundary before changing anything.
- Verify tool paths from the same execution context that failed.
- Use immutable build tags and verify registry digests.
- Store credentials in Jenkins; never embed access keys or secret values in source.
- Use a dedicated kubeconfig for automation.
- Inspect Kubernetes Events instead of guessing from high-level pod states.
- Establish cluster prerequisites before expecting an application pipeline to update them.
- Verify public access at the application endpoint, not only with `kubectl rollout status`.
- Delete chargeable lab resources immediately and verify deletion independently.

## Production improvements

The lab intentionally chose simple mechanisms. A production version should improve them:

- Run Jenkins on a controlled agent image with pinned Docker, AWS CLI, and kubectl versions.
- Prefer an IAM role, workload identity, or short-lived federation over a long-lived IAM access key.
- Apply least-privilege IAM policies for only the required ECR and EKS actions.
- Build and push a multi-architecture image, or ensure the build platform matches the target fleet.
- Use image digests for deployment immutability where appropriate.
- Manage namespace, ConfigMap, Secret metadata, Deployment, Service, and add-ons declaratively with GitOps or IaC.
- Use an external secret manager rather than literal secret creation commands.
- Use readiness/liveness probes and verify the HTTP health endpoint from the pipeline.
- Prefer Ingress/ALB or a private entry path over a publicly open NodePort.
- Restrict inbound CIDRs; never leave a lab `0.0.0.0/0` rule longer than needed.
- Add lifecycle policies to ECR so old build tags do not accumulate indefinitely.
- Add Jenkins `post` blocks for notifications, cleanup, and diagnostic capture.
- Add concurrency controls so two builds do not race to update the same Deployment.

## Debugging order that worked

```text
Pipeline stage boundary
→ resource existence/status
→ pod state
→ pod Events
→ architecture/auth/network evidence
→ smallest fix
→ repeat original verification
```
