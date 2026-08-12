# Day 9 Best Practices

Day 9 proved the deployment path. These practices turn that path into something safer, more repeatable, and closer to production.

## Identity and access

- Do not use the AWS root user for routine work.
- Prefer IAM Identity Center or another federation method with short-lived role credentials over long-lived IAM access keys.
- Require MFA and rotate or remove unused credentials.
- Scope cluster-provisioning permissions to the required EKS, CloudFormation, EC2, IAM, Auto Scaling, and related resources.
- Restrict `iam:PassRole` to named roles and intended AWS services.
- Review who receives Kubernetes access; AWS authentication and Kubernetes RBAC solve different parts of authorization.

## Infrastructure as code

- Keep the `eksctl` configuration in source control and review dry-run output before creation.
- Pin and deliberately upgrade the Kubernetes version after checking EKS support and add-on compatibility.
- Separate reusable values such as account, region, cluster name, and image digest from environment-specific secrets.
- Prefer Terraform, CloudFormation, or a controlled `eksctl` workflow over manual console-only changes for repeatable environments.
- Tag all AWS resources with owner, project, environment, and expiry metadata.
- Treat CloudFormation events as primary provisioning evidence and preserve useful failure notes.

## Cluster networking

- Run production worker nodes in private subnets across multiple Availability Zones.
- Restrict the Kubernetes API endpoint to approved networks or use private access.
- Expose applications through a managed load balancer or ingress with TLS, health checks, DNS, and controlled security groups.
- Never open the entire NodePort range when one port is sufficient.
- Avoid `0.0.0.0/0` for administrative or lab ports; use a known `/32` source or a trusted network.
- Apply Kubernetes NetworkPolicies where the selected networking stack enforces them.

## Container images and ECR

- Make the target platform explicit in CI: `linux/amd64`, `linux/arm64`, or a reviewed multi-architecture build.
- Use immutable version tags and deploy by digest for the strongest reproducibility.
- Record the source commit, build ID, base-image version, and image digest.
- Scan images, keep base images patched, run as a non-root user, and minimize installed packages.
- Sign artifacts and verify provenance where the delivery platform supports it.
- Configure an ECR lifecycle policy so unneeded images do not accumulate indefinitely.
- Prefer `imagePullPolicy: IfNotPresent` with immutable tags/digests; do not rely on mutable tags to signal a new release.

## Kubernetes workload design

The Day 9 manifest is intentionally small. A production Pod template should add:

```yaml
securityContext:
  runAsNonRoot: true
  seccompProfile:
    type: RuntimeDefault

containers:
  - name: arun-flask-container
    image: <ECR_URI>@sha256:<DIGEST>
    ports:
      - name: http
        containerPort: 5000
    readinessProbe:
      httpGet:
        path: /
        port: http
      initialDelaySeconds: 3
      periodSeconds: 5
    livenessProbe:
      httpGet:
        path: /
        port: http
      initialDelaySeconds: 10
      periodSeconds: 10
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
      limits:
        memory: 256Mi
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
```

The application and image must support a read-only filesystem before enabling it. CPU limits are workload-dependent and should be chosen using measurement rather than copied blindly.

Also consider:

- a production WSGI server such as Gunicorn instead of Flask's development server;
- `RollingUpdate` settings appropriate to capacity and availability;
- a PodDisruptionBudget for voluntary disruptions;
- topology spread constraints or anti-affinity across nodes and zones;
- a Horizontal Pod Autoscaler supported by realistic resource requests;
- graceful shutdown and a sufficient `terminationGracePeriodSeconds`;
- ServiceAccounts and workload-specific AWS permissions through EKS Pod Identity or IRSA.

## Configuration and secrets

- Keep non-sensitive configuration in ConfigMaps, but version and review it like code.
- Never commit plaintext production credentials or generated Secret manifests containing real values.
- Use AWS Secrets Manager or Systems Manager Parameter Store with an approved external-secrets mechanism.
- Enable Kubernetes Secret encryption at rest with KMS where required.
- Grant the smallest RBAC access to Secrets and audit access.
- Plan rotation; a secret that cannot be rotated safely is an operational liability.
- Remember that environment-variable changes require replacement Pods.

## Verification and observability

- Validate manifests with server-side dry-run before apply.
- Check rollout status with a timeout and fail the delivery process if it does not become healthy.
- Verify Service endpoints, not only that the Service object exists.
- Centralize application and Kubernetes logs instead of relying on transient `kubectl logs` output.
- Collect CPU, memory, restart, latency, traffic, and error metrics with actionable alerts.
- Add distributed request IDs so a browser request can be correlated with a specific Pod and log record.
- Test rollback and recovery before an incident.

## Delivery workflow

```text
commit
  -> test
  -> build for declared platforms
  -> scan and sign
  -> push immutable image to ECR
  -> update digest in reviewed manifest
  -> server-side validation
  -> deploy
  -> rollout and health verification
  -> automatic rollback or alert on failure
```

The most important improvement over Day 9's manual path is not simply more automation. It is preserving evidence and enforcing the same checks—identity, platform, artifact, configuration, rollout, access, and cleanup—every time.

