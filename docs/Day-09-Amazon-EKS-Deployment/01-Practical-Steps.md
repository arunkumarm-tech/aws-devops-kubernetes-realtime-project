# Day 9 Practical Steps

This guide follows the order used during the session. Commands assume macOS, AWS Region `us-east-1`, and execution from the repository root.

## 1. Use an IAM user instead of root

The AWS account root user should be reserved for account-level tasks that require it. An IAM user was created for CLI work, and its access keys were configured locally.

Before creating credentials, the user needs permissions for the lab resources: EKS, EC2, IAM role creation/passing, CloudFormation, Auto Scaling, and ECR. Broad administrator access may be convenient in a temporary learning account, but a long-lived environment should use a reviewed least-privilege role and short-lived credentials.

Configure and verify the CLI:

```bash
aws configure
aws sts get-caller-identity
aws configure get region
```

Expected identity shape:

```json
{
  "UserId": "...",
  "Account": "<AWS_ACCOUNT_ID>",
  "Arn": "arn:aws:iam::<AWS_ACCOUNT_ID>:user/<IAM_USER>"
}
```

The important check is that the ARN identifies the intended IAM principal, not the root user, and that the active region is `us-east-1`.

## 2. Verify local tools

```bash
aws --version
kubectl version --client
docker version
eksctl version
```

If `eksctl` is not installed on macOS:

```bash
brew tap weaveworks/tap
brew install weaveworks/tap/eksctl
eksctl version
```

Package locations can change over time. If Homebrew reports that the tap or formula moved, use the current command shown by the official `eksctl` installation instructions.

## 3. Define the EKS cluster

The session produced `eks/eks-cluster.yaml`:

```yaml
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig

metadata:
  name: arun-eks-cluster
  region: us-east-1
  version: "1.35"

vpc:
  nat:
    gateway: Disable
  clusterEndpoints:
    publicAccess: true
    privateAccess: false

managedNodeGroups:
  - name: arun-eks-ng
    instanceType: t3.small
    desiredCapacity: 2
    minSize: 2
    maxSize: 2
    volumeType: gp3
    volumeSize: 20
    privateNetworking: false
```

Why these fields mattered:

| Setting | Purpose |
|---|---|
| `region` | Keeps all Day 9 resources in `us-east-1` |
| Kubernetes `version` | Pins the intended EKS control-plane version; confirm AWS currently offers it before reuse |
| managed node group | Lets EKS manage the EC2 worker lifecycle |
| `t3.small` | Replaced the unsuccessful `t3.medium` choice in this lab |
| fixed capacity of 2 | Keeps the exercise predictable; production would normally allow scaling |
| `gp3`, 20 GiB | Uses general-purpose EBS volumes for worker root disks |
| NAT disabled/public workers | Reduced lab infrastructure, but is not the preferred production topology |

## 4. Preview before creation

```bash
eksctl create cluster -f eks/eks-cluster.yaml --dry-run
```

Dry-run renders and validates the configuration that `eksctl` intends to use. It is a planning aid: it does not prove that EC2 capacity, quotas, IAM permissions, or every downstream CloudFormation operation will succeed.

Review the preview for the cluster name, region, Kubernetes version, node-group name, instance type, capacity, networking, and disk settings.

## 5. Create the cluster

```bash
eksctl create cluster -f eks/eks-cluster.yaml
```

`eksctl` creates CloudFormation stacks for the EKS control plane and node group, waits for resources, and updates kubeconfig when successful. This takes much longer than creating local Kubernetes objects.

The first attempt used `t3.medium` and failed during the node-group stage. The useful response was not to rerun blindly; CloudFormation events were inspected to identify the failing resource and reason.

After changing the configuration to `t3.small`, creation was run again. Verify the result:

```bash
aws eks list-clusters --region us-east-1
eksctl get cluster --region us-east-1
eksctl get nodegroup --cluster arun-eks-cluster --region us-east-1
kubectl config current-context
kubectl get nodes -o wide
```

Expected observations:

- `arun-eks-cluster` is listed as active.
- Two nodes eventually report `Ready`.
- The nodes use the configured managed node group.
- `kubectl` targets the EKS context, not the earlier Docker Desktop context.

## 6. Diagnose the image architecture before deployment

The Mac used Apple Silicon, so a normal local Docker build produced an ARM64 image. The selected EC2 workers were AMD64. An ARM64-only executable cannot start on AMD64 nodes, commonly producing an `exec format error`.

Inspect a local image:

```bash
docker image inspect arun-jenkins-flask-app:v1 \
  --format '{{.Os}}/{{.Architecture}}'
```

Inspect an ECR manifest when needed:

```bash
aws ecr batch-get-image \
  --repository-name arun-jenkins-flask-app \
  --image-ids imageTag=day9-amd64 \
  --region us-east-1
```

## 7. Build and push an AMD64 image with Buildx

Set reusable shell values:

```bash
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
IMAGE_URI="${ECR_REGISTRY}/arun-jenkins-flask-app:day9-amd64"
```

Authenticate Docker to ECR:

```bash
aws ecr get-login-password --region "$AWS_REGION" | \
  docker login --username AWS --password-stdin "$ECR_REGISTRY"
```

Build for the node architecture and push directly:

```bash
docker buildx build \
  --platform linux/amd64 \
  -f docker/Dockerfile \
  -t "$IMAGE_URI" \
  --push .
```

Confirm the tag exists:

```bash
aws ecr describe-images \
  --repository-name arun-jenkins-flask-app \
  --image-ids imageTag=day9-amd64 \
  --region us-east-1 \
  --query 'imageDetails[0].{Tags:imageTags,Digest:imageDigest,Pushed:imagePushedAt}'
```

`--platform linux/amd64` is the critical correction. `--push` sends the Buildx result to ECR; without `--load`, a single-platform result may not appear in the classic local image list.

## 8. Update the Kubernetes Deployment

The Deployment was changed from the local image name to the complete ECR URI:

```yaml
image: <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/arun-jenkins-flask-app:day9-amd64
imagePullPolicy: IfNotPresent
```

The repository currently contains the session-specific account ID in `kubernetes/flask-deployment.yaml`. For another account, replace it or template the manifest before applying.

Confirm the active context again:

```bash
kubectl config current-context
kubectl cluster-info
```

## 9. Recreate namespace, ConfigMap, and Secret

Kubernetes objects from Docker Desktop do not automatically move to EKS. Create the namespace:

```bash
kubectl create namespace arun-devops
```

For idempotent ConfigMap creation:

```bash
kubectl create configmap arun-flask-config \
  --from-literal=APP_ENV=development \
  --from-literal=APP_MESSAGE='Running from Amazon EKS' \
  -n arun-devops \
  --dry-run=client -o yaml | kubectl apply -f -
```

Create the Secret without placing real values in source control:

```bash
read -r DB_USERNAME
read -rs DB_PASSWORD
echo

kubectl create secret generic arun-flask-secret \
  --from-literal=DB_USERNAME="$DB_USERNAME" \
  --from-literal=DB_PASSWORD="$DB_PASSWORD" \
  -n arun-devops \
  --dry-run=client -o yaml | kubectl apply -f -

unset DB_USERNAME DB_PASSWORD
```

Check names and keys without printing secret data:

```bash
kubectl get configmap arun-flask-config -n arun-devops
kubectl describe secret arun-flask-secret -n arun-devops
```

## 10. Deploy the application and Service

Validate against the live API and apply:

```bash
kubectl apply --dry-run=server -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl apply -f kubernetes/flask-service.yaml
```

Wait for and inspect the rollout:

```bash
kubectl rollout status deployment/arun-flask-deployment -n arun-devops --timeout=5m
kubectl get deployment,pods,service -n arun-devops -o wide
kubectl get endpoints arun-flask-service -n arun-devops
```

Expected shape:

```text
deployment.apps/arun-flask-deployment   2/2   2   2   ...
pod/arun-flask-deployment-...           1/1   Running   0   ...
service/arun-flask-service              NodePort ... 80:<NODE_PORT>/TCP
```

If Pods are not healthy, do not continue to networking. Inspect them first:

```bash
kubectl describe pod -n arun-devops <POD_NAME>
kubectl logs -n arun-devops <POD_NAME>
```

## 11. Open the assigned NodePort for the lab

Obtain the assigned port:

```bash
NODE_PORT=$(kubectl get service arun-flask-service \
  -n arun-devops \
  -o jsonpath='{.spec.ports[0].nodePort}')
echo "$NODE_PORT"
```

Find the worker instance and security group through the AWS CLI or EC2 console. Before adding a rule, confirm that the security group belongs to the EKS worker nodes—not the cluster control plane.

For a short lab, add an inbound TCP rule for exactly `$NODE_PORT`, sourced only from the operator's current public IP as `/32`. Avoid opening the full NodePort range (`30000-32767`) or `0.0.0.0/0` unless a disposable exercise explicitly requires it.

Example after identifying the security-group ID and trusted source CIDR:

```bash
aws ec2 authorize-security-group-ingress \
  --group-id <WORKER_SECURITY_GROUP_ID> \
  --protocol tcp \
  --port "$NODE_PORT" \
  --cidr <YOUR_PUBLIC_IP>/32 \
  --region us-east-1
```

Find a public worker address:

```bash
kubectl get nodes -o wide
```

Then visit:

```text
http://<WORKER_PUBLIC_IP>:<NODE_PORT>
```

The successful browser response proved the whole path: public IP, security group, NodePort, Service selector, Service endpoint, Pod, container port, and Flask process.

## 12. Final runtime verification

```bash
kubectl get all -n arun-devops
kubectl describe deployment arun-flask-deployment -n arun-devops
kubectl describe service arun-flask-service -n arun-devops
kubectl logs -l app=arun-flask -n arun-devops --tail=50 --prefix
```

Useful success signals are two available replicas, Running/Ready Pods, populated Service endpoints, no repeated restarts, and HTTP access lines after the browser request.

## 13. Clean up

The cluster was deleted after verification to stop ongoing EKS and EC2 costs:

```bash
eksctl delete cluster \
  --name arun-eks-cluster \
  --region us-east-1 \
  --wait
```

Do not close the exercise on the deletion command alone. Run the post-cleanup checks in [Cost Optimization](06-Cost-Optimization.md). The ECR repository was intentionally retained for later sessions.

