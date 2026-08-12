# Day 9 Cost Optimization and Cleanup

EKS learning environments should have a deliberate lifetime. Stopping application Pods does not stop charges for the control plane or worker infrastructure.

## What can create cost

| Resource | Cost behavior | Day 9 handling |
|---|---|---|
| EKS control plane | Charged while the cluster exists | Deleted after the exercise |
| EC2 worker nodes | Compute charge while running | Removed with the managed node group |
| EBS worker volumes | Storage charge while retained | Expected to delete with nodes; verify |
| Public IPv4 | May be charged while allocated/in use | Removed with workers; verify addresses |
| NAT gateway | Hourly and data-processing charges | Disabled in the lab config |
| Load balancer | Hourly/capacity charges | Not expected because NodePort was used |
| CloudWatch | Logs, metrics, and retention can cost | Review log groups and retention |
| ECR | Image storage and data transfer | Repository intentionally retained |
| Data transfer | Depends on path and volume | Minimal for this exercise |

AWS pricing and free-tier rules change. Check current pricing before assuming an instance type or service is free.

## Choices made for the lab

- Two `t3.small` workers provided a useful Kubernetes exercise without larger instances.
- `gp3` volumes were kept small at 20 GiB.
- NAT gateways were disabled; the public-worker design avoided NAT cost for this temporary environment.
- A NodePort was used instead of provisioning a load balancer.
- The cluster was deleted on the same day.
- ECR was kept because later deployment work will reuse the image repository.

These choices reduce lab cost but are not all production recommendations. Private workers behind controlled egress and a load balancer usually provide a stronger production architecture even though they add cost.

## Delete the cluster

```bash
eksctl delete cluster \
  --name arun-eks-cluster \
  --region us-east-1 \
  --wait
```

`--wait` keeps the command attached until CloudFormation deletion finishes or reports a failure. If deletion fails, inspect the stack event reason before manually changing resources.

## Post-cleanup verification

The following checks are intentionally read-only.

### EKS clusters

```bash
aws eks list-clusters --region us-east-1
```

Expected:

```json
{
  "clusters": []
}
```

### Non-terminated EC2 instances

```bash
aws ec2 describe-instances \
  --region us-east-1 \
  --filters Name=instance-state-name,Values=pending,running,stopping,stopped \
  --query 'Reservations[].Instances[].{Id:InstanceId,State:State.Name,Type:InstanceType,Name:Tags[?Key==`Name`]|[0].Value}' \
  --output table
```

Expected for an otherwise empty lab account: no matching instances. If the account hosts unrelated workloads, identify ownership by tags before taking action.

### Active EKS CloudFormation stacks

```bash
aws cloudformation list-stacks \
  --region us-east-1 \
  --stack-status-filter CREATE_IN_PROGRESS CREATE_COMPLETE UPDATE_IN_PROGRESS UPDATE_COMPLETE ROLLBACK_IN_PROGRESS ROLLBACK_COMPLETE DELETE_IN_PROGRESS DELETE_FAILED \
  --query 'StackSummaries[?starts_with(StackName, `eksctl-arun-eks-cluster`)].{Name:StackName,Status:StackStatus}' \
  --output table
```

No `CREATE_COMPLETE`, `ROLLBACK_COMPLETE`, or `DELETE_FAILED` Day 9 stack should remain. A brief `DELETE_IN_PROGRESS` is normal while cleanup continues.

### Auto Scaling groups

```bash
aws autoscaling describe-auto-scaling-groups \
  --region us-east-1 \
  --query 'AutoScalingGroups[?contains(AutoScalingGroupName, `arun-eks`)].{Name:AutoScalingGroupName,Desired:DesiredCapacity}' \
  --output table
```

Expected: no Day 9 Auto Scaling group.

### Load balancers

```bash
aws elbv2 describe-load-balancers \
  --region us-east-1 \
  --query 'LoadBalancers[].{Name:LoadBalancerName,Type:Type,State:State.Code}' \
  --output table
```

The session used NodePort, so no application load balancer was expected. Do not delete any unrelated load balancer based only on this expectation.

### NAT gateways

```bash
aws ec2 describe-nat-gateways \
  --region us-east-1 \
  --filter Name=state,Values=pending,available,deleting,failed \
  --query 'NatGateways[].{Id:NatGatewayId,State:State,Vpc:VpcId}' \
  --output table
```

The cluster configuration disabled NAT. This check protects against leftovers from a partial or earlier setup.

### Unattached EBS volumes

```bash
aws ec2 describe-volumes \
  --region us-east-1 \
  --filters Name=status,Values=available \
  --query 'Volumes[].{Id:VolumeId,SizeGiB:Size,Type:VolumeType,Created:CreateTime}' \
  --output table
```

An available volume is not automatically safe to delete. Confirm tags and ownership first.

### Elastic IP addresses

```bash
aws ec2 describe-addresses \
  --region us-east-1 \
  --query 'Addresses[].{AllocationId:AllocationId,PublicIp:PublicIp,AssociationId:AssociationId}' \
  --output table
```

Review unassociated allocations carefully because they can incur charges.

### ECR repository intentionally retained

```bash
aws ecr describe-repositories \
  --region us-east-1 \
  --query 'repositories[].repositoryName'

aws ecr describe-images \
  --repository-name arun-jenkins-flask-app \
  --region us-east-1 \
  --query 'imageDetails[].{Tags:imageTags,SizeBytes:imageSizeInBytes,Pushed:imagePushedAt}' \
  --output table
```

Keeping ECR is a conscious tradeoff: it avoids rebuilding the artifact for the next session but continues to consume registry storage.

## Ongoing controls

- Set an AWS Budget with email alerts before creating learning infrastructure.
- Use mandatory owner, project, and expiry tags.
- Schedule a daily inventory check for forgotten EKS, EC2, NAT gateway, and load-balancer resources.
- Set short CloudWatch log retention for temporary labs.
- Add an ECR lifecycle rule that keeps important release tags while expiring old untagged images.
- Prefer deleting and recreating a lab cluster over leaving it idle for days.
- Review all regions used by the account; a clean `us-east-1` check says nothing about another region.

## Final checklist

- [x] EKS cluster deletion requested and awaited
- [ ] EKS cluster list is empty in `us-east-1`
- [ ] No Day 9 EC2 workers remain
- [ ] No active or failed Day 9 CloudFormation stacks remain
- [ ] No Day 9 Auto Scaling group remains
- [ ] No unexpected load balancer or NAT gateway remains
- [ ] No orphaned Day 9 EBS volume or Elastic IP remains
- [x] `arun-jenkins-flask-app` ECR repository intentionally retained
- [ ] AWS Billing and Cost Management dashboard checked after usage data updates

The unchecked items are verification actions, not claims that the documentation process queried the live AWS account.

