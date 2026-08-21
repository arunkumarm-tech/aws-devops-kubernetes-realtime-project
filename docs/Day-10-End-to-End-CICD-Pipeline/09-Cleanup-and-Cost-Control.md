# 09 — Cleanup and Cost Control

## Cost decisions during the lab

- The EKS dry run incurred no new infrastructure cost.
- Real cluster creation started EKS control-plane charges.
- The managed node group added two EC2 instances and two 20 GiB gp3 volumes.
- NAT Gateway was disabled in the config to avoid NAT hourly/data-processing charges.
- NodePort avoided creating an AWS load balancer.
- The temporary security-group rule itself was not a separately billed service.
- ECR storage was comparatively small but not free.

## Delete the cluster

After the final public health check:

```bash
eksctl delete cluster \
  --name arun-eks-cluster \
  --region us-east-1
```

Final `eksctl` output included:

```text
will delete stack "eksctl-arun-eks-cluster-cluster"
all cluster resources were deleted
```

Deletion success was not accepted without independent checks.

## Verification commands and actual state

```bash
aws eks list-clusters --region us-east-1
```

Actual: `{"clusters": []}`.

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters Name=instance-state-name,Values=running \
  --query 'Reservations[].Instances[].InstanceId' \
  --output text
```

Actual: no output.

```bash
aws cloudformation list-stacks \
  --region us-east-1 \
  --stack-status-filter CREATE_COMPLETE CREATE_IN_PROGRESS UPDATE_COMPLETE ROLLBACK_COMPLETE \
  --query 'StackSummaries[].StackName' \
  --output text

aws autoscaling describe-auto-scaling-groups \
  --region us-east-1 \
  --query 'AutoScalingGroups[].AutoScalingGroupName' \
  --output text

aws ec2 describe-nat-gateways \
  --region us-east-1 \
  --filter Name=state,Values=available,pending \
  --query 'NatGateways[].NatGatewayId' \
  --output text

aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[].LoadBalancerName' \
  --output text

aws ec2 describe-volumes \
  --region us-east-1 \
  --filters Name=status,Values=available \
  --query 'Volumes[].VolumeId' \
  --output text

aws ec2 describe-addresses \
  --region us-east-1 \
  --query 'Addresses[].PublicIp' \
  --output text
```

All returned no resources in the recorded session. The final verified state was:

```text
EKS clusters        none
Running EC2         none
Active CF stacks    none
Auto Scaling Groups none
NAT Gateways        none
Load Balancers      none
Unattached EBS      none
Elastic IPs         none
```

## Intentionally retained resource

The ECR repository and images—including build 8, 9, 11, 12, and 13 references—were intentionally kept temporarily for documentation. The agreed follow-up was to delete ECR after documentation and any desired screenshots/digest records were complete. Therefore the accurate Day 10 closeout is: expensive compute/network infrastructure removed; ECR pending final cleanup.
