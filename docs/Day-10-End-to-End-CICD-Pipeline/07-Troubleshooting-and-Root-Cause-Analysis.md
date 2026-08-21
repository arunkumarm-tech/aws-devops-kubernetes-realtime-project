# 07 — Troubleshooting and Root-Cause Analysis

## Failure → investigation → root cause → fix → verification

| Failure | Investigation | Root cause | Fix | Verification |
|---|---|---|---|---|
| Jenkins: `docker: command not found` | `which docker` | Jenkins service PATH omitted `/usr/local/bin` | Add `/usr/local/bin` to pipeline PATH | Build 3 created `build-3` |
| Jenkins could not yet use AWS credential type | Inspect credential `Kind` list | AWS Credentials plugin absent | Install plugin, restart, add global AWS credential | `aws sts get-caller-identity` worked with masked variables |
| Risk that AWS CLI would be unavailable | `which aws` | Homebrew AWS CLI lived in `/opt/homebrew/bin` | Add `/opt/homebrew/bin` to PATH | AWS CLI Check succeeded |
| ECR table query: `Row should have 2 elements` | Review JMESPath shape | Some image detail rows did not project two table cells | Query a known tag and return an object | Build 8 tag/digest/size verified |
| `AlreadyExistsException` for cluster stack | Inspect CloudFormation status | A second cluster create was started while the first stack existed | Do not delete; let original complete | Control-plane stack completed |
| Cluster existed with no workers | `aws eks list-nodegroups` | Interrupted creation had not created node group | `eksctl create nodegroup --config-file ...` | Node group became active and nodes appeared |
| Both nodes `NotReady` | Check `kube-system` and `aws eks list-addons` | Core EKS add-ons were absent | Install `vpc-cni`, then `kube-proxy`, then `coredns` | Nodes Ready; six system pods Running |
| `kubectl set image` would fail | `kubectl get deployment -n arun-devops` | Fresh cluster had no baseline Deployment | Apply `flask-deployment.yaml` | Two baseline pods Running |
| Build 11 rollout timed out | `kubectl get pods`, then `kubectl describe pod` | New image entered `ImagePullBackOff` | Inspect exact pull event | Event exposed platform mismatch |
| `no match for platform in manifest` | Compare Mac build host and node kernel | Apple Silicon build was ARM64; `t3.small` was AMD64 | buildx with `--platform linux/amd64 --load` | Build 12 rollout succeeded |
| Public curl hung | Check Service endpoints, node SG, and permissions | NodePort 30094 absent from inbound rules | Add temporary TCP 30094 rule | `/` and `/health` worked publicly |
| Jenkins stages nested or outside `stages` | Inspect `cat`, `tail`, `sed`, and diff | Missing/misplaced Groovy braces during manual editing | Correct braces before commit | Subsequent pipeline parsed and ran |

## Detailed build 11 diagnosis

The rollout output alone showed only a symptom:

```text
Waiting for deployment ... 1 out of 2 new replicas have been updated...
error: timed out waiting for the condition
```

The next command separated the old healthy ReplicaSet from the new failing pod:

```bash
kubectl get pods -n arun-devops -o wide
```

Then the failing pod was described:

```bash
kubectl describe pod arun-flask-deployment-69c846444f-694hf -n arun-devops
```

The decisive event was:

```text
Failed to pull and unpack image ... no match for platform in manifest: not found
```

This sequence matters: rollout timeout is not a root cause, and `ImagePullBackOff` is still only a category. Kubernetes Events supplied the actionable cause.

## What happened internally during recovery

- `vpc-cni` deployed the `aws-node` DaemonSet and restored VPC networking for pods; node readiness changed immediately.
- `kube-proxy` restored Service forwarding rules used by ClusterIP and NodePort traffic.
- CoreDNS restored Kubernetes service-name resolution.
- A Deployment rollout created a new ReplicaSet, started new pods, waited for readiness, and then terminated old pods. Old pods in `Terminating` during build 13 were expected rolling-update behavior.
