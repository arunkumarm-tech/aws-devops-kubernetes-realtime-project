# Day 9 Learning Notes

## The main outcome

The Flask application moved from local Kubernetes to Amazon EKS and was reached from a browser. More importantly, the session connected the complete delivery chain:

```text
IAM identity
  -> eksctl configuration
  -> CloudFormation
  -> EKS control plane and EC2 workers
  -> Buildx AMD64 image
  -> Amazon ECR
  -> Kubernetes Deployment
  -> ConfigMap and Secret
  -> NodePort Service
  -> EC2 security group
  -> browser response
  -> cluster cleanup
```

## Real observations

### A dry-run is valuable, but it is not a deployment

The dry-run made the intended cluster visible before AWS resources were created. It could catch configuration mistakes, but it could not promise node capacity, account quota, permission correctness, or downstream resource success.

### Managed services still require infrastructure knowledge

EKS manages the Kubernetes control plane, but the exercise still required understanding IAM, CloudFormation, EC2 instance types, Auto Scaling, VPC networking, security groups, EBS, ECR, and Kubernetes. “Managed” moves responsibilities; it does not remove them.

### Read the first useful failure

The failed node group produced follow-on rollback messages. The actionable detail was the earliest relevant `CREATE_FAILED` event and its status reason. Later cancellation errors were consequences.

### The successful fix is not always the universal cause

Moving from `t3.medium` to `t3.small` made this lab succeed. That observation belongs in the record. It should not be generalized into “EKS does not support `t3.medium`”; future diagnosis should still use the account's actual launch and CloudFormation evidence.

### Container portability has a platform boundary

Containers package user-space dependencies, but they still depend on the host kernel and CPU instruction set. Building on an ARM64 Mac without an explicit platform produced the wrong artifact for AMD64 EC2 workers. Buildx turned platform choice into an explicit, reproducible build input.

### Cluster state does not migrate automatically

The ConfigMap and Secret worked in Docker Desktop but were absent in EKS. The repository and secret-delivery process—not a developer's current cluster—must be the source of truth for recreating an environment.

### External access crosses several control planes

Creating a NodePort Service was only one step. Success required a Ready Pod, matching labels, populated endpoints, correct ports, worker addressing, and an AWS security-group rule. The browser response was an end-to-end test of all those links.

### Cleanup is part of deployment

A learning cluster left idle is still production infrastructure from the billing system's point of view. The work was not finished until the cluster deletion completed and supporting resources were checked.

## Commands worth remembering

```bash
# Confirm AWS identity
aws sts get-caller-identity

# Preview and create EKS
eksctl create cluster -f eks/eks-cluster.yaml --dry-run
eksctl create cluster -f eks/eks-cluster.yaml

# Inspect cluster and nodes
kubectl config current-context
kubectl get nodes -o wide

# Build the correct platform and push
docker buildx build --platform linux/amd64 -f docker/Dockerfile -t <ECR_URI>:day9-amd64 --push .

# Validate and deploy
kubectl apply --dry-run=server -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-service.yaml

# Verify rollout and routing
kubectl rollout status deployment/arun-flask-deployment -n arun-devops
kubectl get pods,service,endpoints -n arun-devops -o wide

# Investigate provisioning failure
aws cloudformation describe-stack-events --stack-name <STACK_NAME> --region us-east-1

# Delete the lab
eksctl delete cluster --name arun-eks-cluster --region us-east-1 --wait
```

## Troubleshooting method reinforced today

1. Confirm the target: AWS account, region, kubeconfig context, namespace, and resource name.
2. Read current state before changing it.
3. Find the lowest layer that is still healthy.
4. Read structured events and status reasons.
5. Change one relevant variable.
6. Re-run the narrowest useful verification.
7. Record the observed result without overstating the cause.

For this session, that method appeared twice:

```text
Cluster creation failed
  -> CloudFormation events
  -> node-group/instance evidence
  -> instance type changed
  -> nodes became Ready

Container failed
  -> Pod status and logs
  -> image architecture compared with node architecture
  -> AMD64 image built and pushed
  -> rollout became healthy
```

## Skills practiced

- AWS IAM identity hygiene and CLI verification
- Declarative EKS configuration with `eksctl`
- CloudFormation event analysis
- Managed EC2 node-group provisioning
- Cross-platform Docker builds with Buildx
- Private image publishing and inspection in ECR
- Kubernetes context and namespace discipline
- ConfigMap and Secret recreation
- Deployment rollout and Pod diagnosis
- Service selectors, endpoints, NodePort, and security groups
- Browser-based end-to-end verification
- AWS resource cleanup and cost awareness

## Resume-ready project statement

Provisioned and troubleshot an Amazon EKS cluster in `us-east-1` using `eksctl` and CloudFormation-backed managed EC2 node groups; resolved node-group provisioning and ARM64/AMD64 container compatibility issues; published a platform-correct Flask image to Amazon ECR; deployed a two-replica Kubernetes workload with ConfigMap and Secret injection; exposed and verified the service through NodePort and controlled security-group ingress; and performed post-lab infrastructure cleanup checks to limit AWS cost.

## What to improve next

1. Move workers into private subnets across multiple Availability Zones.
2. Replace direct NodePort access with an AWS Load Balancer Controller-managed ingress and TLS.
3. Add production WSGI serving, health probes, resource requests, and security contexts.
4. Replace terminal-created secrets with AWS Secrets Manager and a controlled workload identity.
5. Automate tests, multi-platform builds, scanning, signing, ECR publishing, manifest updates, rollout checks, and rollback.
6. Add metrics, centralized logs, alerts, budgets, and expiry-based lab cleanup.

## Day 9 completion checklist

- [x] IAM identity used instead of root for normal work
- [x] AWS CLI and `eksctl` verified
- [x] Cluster configuration dry-run reviewed
- [x] Failed node group investigated through CloudFormation
- [x] Instance type corrected from `t3.medium` to `t3.small`
- [x] Two EKS worker nodes became available
- [x] ARM64/AMD64 mismatch diagnosed
- [x] `linux/amd64` image pushed to ECR as `day9-amd64`
- [x] Deployment updated to use ECR
- [x] Namespace, ConfigMap, and Secret recreated in EKS
- [x] Deployment and NodePort Service applied
- [x] Worker security-group rule added for the assigned NodePort
- [x] Application verified in a browser
- [x] Cluster deletion initiated and awaited
- [x] ECR repository intentionally retained

