# Day 9 Troubleshooting Record

The most valuable Day 9 work happened between the first failure and the final browser response. This record separates symptoms from evidence and avoids treating guesses as causes.

## EKS node group failed with `t3.medium`

**Symptom**

The EKS control-plane work began, but managed node-group creation did not complete. The related CloudFormation stack entered a failed or rollback state.

**Investigation**

```bash
aws cloudformation describe-stack-events \
  --stack-name <NODEGROUP_STACK_NAME> \
  --region us-east-1 \
  --query 'StackEvents[?ResourceStatus==`CREATE_FAILED`].[Timestamp,LogicalResourceId,ResourceType,ResourceStatusReason]' \
  --output table
```

Also inspect the Auto Scaling activity and instance launches if the event points there:

```bash
aws autoscaling describe-scaling-activities \
  --auto-scaling-group-name <ASG_NAME> \
  --region us-east-1
```

**Session correction**

The node-group instance type was changed from `t3.medium` to `t3.small`, the failed stack was allowed to roll back or was deleted, and creation was retried successfully.

**Important nuance**

`t3.medium` is not inherently unsupported by EKS. A failure can depend on account quotas, regional/AZ capacity, launch-template configuration, permissions, or the lab's budget/free-tier constraints. The CloudFormation `ResourceStatusReason` is the authority for the specific attempt. Changing instance type was the successful session fix, not a universal rule.

## CloudFormation rollback looked like an `eksctl` failure

**Symptom**

`eksctl create cluster` ended with a stack error, and the cluster was not usable.

**Cause model**

`eksctl` orchestrates AWS resources through CloudFormation. A single failed nested resource—node instance, IAM role, security group, Auto Scaling group, or EKS resource—can cause the stack to roll back.

**Diagnostic sequence**

```bash
aws cloudformation list-stacks \
  --region us-east-1 \
  --stack-status-filter CREATE_IN_PROGRESS CREATE_FAILED ROLLBACK_IN_PROGRESS ROLLBACK_COMPLETE DELETE_FAILED \
  --query 'StackSummaries[].{Name:StackName,Status:StackStatus}' \
  --output table
```

Then inspect the failing stack's events from newest to oldest. Search for the first meaningful `CREATE_FAILED`, rather than using the later cascade of cancellation messages as the root cause.

**Lesson**

Read from the orchestration layer down: `eksctl` output → CloudFormation event → underlying EC2/IAM/Auto Scaling reason.

## Pods failed with `exec format error`

**Symptom**

The image pulled, but the container repeatedly failed to start. Logs or Pod events showed an error similar to:

```text
exec ...: exec format error
```

**Cause**

The original image was built on Apple Silicon as ARM64, while the `t3.small` worker nodes used AMD64. Kubernetes can schedule a container based on declared image metadata, but the kernel cannot execute binaries for the wrong CPU architecture.

**Verification**

```bash
docker image inspect <LOCAL_IMAGE> --format '{{.Os}}/{{.Architecture}}'
kubectl get nodes -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.nodeInfo.architecture}{"\n"}{end}'
```

**Fix**

```bash
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t <ECR_URI>:day9-amd64 \
  --push .
```

Update the Deployment to the new tag, apply it, and watch the rollout.

**Lesson**

Treat architecture as part of the artifact contract. CI should build for the deployment platform, not silently inherit the CI host's architecture.

## `ImagePullBackOff` or `ErrImagePull`

**Possible causes**

- The Deployment contains the wrong account ID, region, repository, or tag.
- The Buildx image was built but not pushed.
- The node IAM role cannot pull from ECR.
- ECR authentication or repository policy is wrong for a cross-account case.

**Checks**

```bash
kubectl describe pod -n arun-devops <POD_NAME>
kubectl get deployment arun-flask-deployment -n arun-devops \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
aws ecr describe-images \
  --repository-name arun-jenkins-flask-app \
  --image-ids imageTag=day9-amd64 \
  --region us-east-1
```

Read the Pod event message before changing credentials. Same-account EKS workers normally pull from ECR through their IAM role; a manually created Kubernetes image-pull Secret is generally not needed for this setup.

## Pods remained Pending

**Likely evidence**

```bash
kubectl get nodes
kubectl describe pod -n arun-devops <POD_NAME>
kubectl get events -n arun-devops --sort-by=.lastTimestamp
```

Common causes include no Ready nodes, insufficient CPU or memory, node taints, incompatible node selectors, or a node group that never joined. A Pending Pod has not started a container, so application logs may not exist yet; scheduler events are more useful.

## ConfigMap or Secret was reported as missing

**Symptom**

Pod events reported that `arun-flask-config` or `arun-flask-secret` was not found.

**Cause**

The objects existed in the local Docker Desktop cluster, not in EKS, or they were created in a different namespace. ConfigMaps and Secrets are namespace-scoped.

**Checks and fix**

```bash
kubectl config current-context
kubectl get configmap,secret -n arun-devops
kubectl get configmap,secret -A | grep arun-flask
```

Recreate them in `arun-devops`, then restart or reapply the Deployment if necessary.

## Browser could not reach the NodePort

Use an inside-out sequence rather than changing several network settings at once.

### 1. Confirm the process and Pods

```bash
kubectl get pods -n arun-devops -o wide
kubectl logs -l app=arun-flask -n arun-devops --tail=50 --prefix
```

### 2. Confirm Service selection and endpoints

```bash
kubectl describe service arun-flask-service -n arun-devops
kubectl get endpoints arun-flask-service -n arun-devops
```

An empty endpoint list usually means the Service selector does not match the Pod labels, or no selected Pod is Ready.

### 3. Test through Kubernetes without public networking

```bash
kubectl port-forward service/arun-flask-service 8081:80 -n arun-devops
```

Open `http://localhost:8081`. If this works, the Pod and Service path are healthy; focus on the node address, NodePort, routing, and security group.

### 4. Confirm external details

```bash
kubectl get service arun-flask-service -n arun-devops
kubectl get nodes -o wide
```

Verify that:

- the URL uses a worker's public IP, not its private address;
- the URL uses the assigned NodePort, not Service port 80 or container port 5000;
- the inbound rule is attached to the worker security group;
- the rule allows TCP on that exact port from the operator's current public IP;
- local or corporate firewalls do not block the connection.

## `kubectl` pointed to Docker Desktop

**Symptom**

AWS resources appeared healthy, but `kubectl get nodes` showed the local cluster or EKS objects appeared missing.

**Fix**

```bash
aws eks update-kubeconfig \
  --name arun-eks-cluster \
  --region us-east-1
kubectl config current-context
kubectl get nodes
```

Always inspect the context before applying or deleting resources when multiple clusters are configured.

## Cleanup did not finish cleanly

**Symptom**

`eksctl delete cluster` returned an error or supporting resources remained.

**Approach**

Inspect CloudFormation `DELETE_FAILED` events. External resources or manual modifications can block deletion. Do not manually remove random resources while a stack is actively deleting; first identify the exact dependency in the event reason.

After deletion, verify EKS clusters, running EC2 instances, active EKS CloudFormation stacks, Auto Scaling groups, load balancers, NAT gateways, and unattached volumes. See [Cost Optimization](06-Cost-Optimization.md).

