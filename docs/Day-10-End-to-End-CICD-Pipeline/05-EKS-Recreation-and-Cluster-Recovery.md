# 05 — EKS Recreation and Cluster Recovery

## Preflight and cost-aware configuration

```bash
aws eks list-clusters --region us-east-1
cat eks/eks-cluster.yaml
eksctl create cluster -f eks/eks-cluster.yaml --dry-run
```

The initial cluster list was empty. The reused configuration specified Kubernetes 1.35, public endpoints, NAT disabled, and a managed node group with two public `t3.small` instances and 20 GiB gp3 volumes.

```yaml
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

The dry run created nothing. The real command started chargeable resources:

```bash
eksctl create cluster -f eks/eks-cluster.yaml
```

## Duplicate CloudFormation stack

While the first cluster command was still running, a second create attempt was made. It failed with:

```text
AlreadyExistsException: Stack [eksctl-arun-eks-cluster-cluster] already exists
```

The correct response was to inspect rather than immediately delete:

```bash
aws cloudformation describe-stacks \
  --stack-name eksctl-arun-eks-cluster-cluster \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus' \
  --output text
```

The original control-plane stack eventually completed. The duplicate failure did not mean the first creation had failed.

## Manual node group creation

The cluster existed but had no node group:

```bash
aws eks list-nodegroups \
  --cluster-name arun-eks-cluster \
  --region us-east-1
```

Actual result: `{"nodegroups": []}`.

The existing config was reused to create only the node group:

```bash
eksctl create nodegroup --config-file eks/eks-cluster.yaml
```

Progress was observed without cancelling the active create:

```bash
aws cloudformation describe-stacks \
  --stack-name eksctl-arun-eks-cluster-nodegroup-arun-eks-ng \
  --region us-east-1 \
  --query 'Stacks[0].StackStatus' \
  --output text

aws cloudformation describe-stack-events \
  --stack-name eksctl-arun-eks-cluster-nodegroup-arun-eks-ng \
  --region us-east-1 \
  --query 'StackEvents[0:8].[Timestamp,ResourceStatus,LogicalResourceId,ResourceStatusReason]' \
  --output table

aws eks describe-nodegroup \
  --cluster-name arun-eks-cluster \
  --nodegroup-name arun-eks-ng \
  --region us-east-1 \
  --query 'nodegroup.{Status:status,Health:health.issues}' \
  --output json
```

## Nodes joined but stayed NotReady

```bash
aws eks update-kubeconfig --name arun-eks-cluster --region us-east-1
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
aws eks list-addons --cluster-name arun-eks-cluster --region us-east-1
```

Both nodes joined but remained `NotReady`; `kube-system` contained no resources and EKS returned `{"addons": []}`. The interrupted creation flow had left the cluster without its core managed add-ons.

## Recovery order

VPC CNI was restored first because node/pod networking was the blocking dependency:

```bash
aws eks create-addon --cluster-name arun-eks-cluster --addon-name vpc-cni --region us-east-1
aws eks describe-addon --cluster-name arun-eks-cluster --addon-name vpc-cni --region us-east-1 \
  --query 'addon.{Status:status,Health:health.issues}' --output json
kubectl get pods -n kube-system -o wide
kubectl get nodes -o wide
```

Once `aws-node` was running on both nodes, both nodes changed immediately to `Ready`.

```bash
aws eks create-addon --cluster-name arun-eks-cluster --addon-name kube-proxy --region us-east-1
aws eks describe-addon --cluster-name arun-eks-cluster --addon-name kube-proxy --region us-east-1 \
  --query 'addon.{Status:status,Health:health.issues}' --output json

aws eks create-addon --cluster-name arun-eks-cluster --addon-name coredns --region us-east-1
aws eks describe-addon --cluster-name arun-eks-cluster --addon-name coredns --region us-east-1 \
  --query 'addon.{Status:status,Health:health.issues}' --output json

kubectl get pods -n kube-system -o wide
```

Final foundation: two `aws-node`, two `kube-proxy`, and two `coredns` pods running; both worker nodes Ready.
