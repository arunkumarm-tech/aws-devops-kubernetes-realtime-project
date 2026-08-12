# Day 9 Interview Questions and Answers

## EKS and provisioning

### 1. What is Amazon EKS?

Amazon EKS is AWS's managed Kubernetes service. AWS operates the Kubernetes control plane, while workloads run on compute such as managed EC2 node groups or AWS Fargate.

### 2. What does `eksctl` do?

`eksctl` turns a cluster configuration or CLI options into the AWS resources required for EKS. It commonly uses CloudFormation to create the control plane, networking, IAM roles, and node groups, and it updates kubeconfig after creation.

### 3. Why use an `eksctl` YAML file?

It makes the intended cluster repeatable and reviewable. The cluster name, region, version, networking, node type, capacity, and disk configuration are visible before provisioning.

### 4. What does `--dry-run` guarantee?

It previews and validates the configuration that `eksctl` plans to use. It does not guarantee that AWS has capacity, that quotas are sufficient, or that every IAM and CloudFormation operation will succeed.

### 5. What is a managed node group?

It is an EKS-managed group of EC2 worker nodes. EKS integrates node provisioning, updates, draining, and Auto Scaling group operations while the nodes run Kubernetes workloads.

### 6. Why did you inspect CloudFormation when cluster creation failed?

Because `eksctl` created the infrastructure through CloudFormation. Stack events expose the exact underlying resource and `ResourceStatusReason`, which is more actionable than the final top-level error.

### 7. Is `t3.medium` unsupported by EKS?

No. The session succeeded after changing from `t3.medium` to `t3.small`, but that does not mean `t3.medium` is generally unsupported. The original failure must be interpreted using its CloudFormation and launch events; quota, capacity, configuration, permission, or lab-budget constraints can differ by account and region.

### 8. Why did you use two workers?

Two nodes demonstrate scheduling and tolerate one node being unavailable better than a single-node lab. They still do not guarantee production high availability; node placement, Availability Zones, Pod disruption budgets, and capacity all matter.

## Identity and security

### 9. Why should the AWS root user not be used for CLI work?

Root has unrestricted account authority and should be reserved for tasks that specifically require it. Normal work should use federated or IAM identities with MFA, short-lived credentials, and least privilege.

### 10. What is `iam:PassRole`, and why can EKS provisioning need it?

It permits a principal to pass an IAM role to an AWS service. Cluster and node-group creation may require service and node roles, so the provisioning identity needs permission to pass only the intended roles.

### 11. How do EKS nodes pull a private ECR image?

The node's IAM role normally has ECR pull permissions. The container runtime obtains authorization and downloads the image layers. In the same-account standard setup, a manually managed Kubernetes registry Secret is usually unnecessary.

### 12. Is a Kubernetes Secret encrypted automatically?

A Secret is base64-encoded in API representations, not inherently protected simply because it is a Secret. Production clusters should enable envelope encryption with KMS where appropriate, restrict RBAC, avoid exposing values, and use an external secrets system for stronger lifecycle management.

## Containers and ECR

### 13. Why did the Apple Silicon image fail on the EKS nodes?

The local build targeted ARM64, while the selected EC2 nodes were AMD64. The worker kernel could not execute binaries for the other architecture, producing an `exec format error`.

### 14. How did Docker Buildx solve it?

Buildx was given `--platform linux/amd64`, so the produced image matched the worker architecture. `--push` published that result directly to ECR.

### 15. What is a multi-architecture image?

It is a manifest list that points to platform-specific image manifests, such as AMD64 and ARM64. The container runtime selects the matching image for the node.

### 16. Why use the full ECR URI in the Deployment?

Kubernetes needs an unambiguous registry, account, region, repository, and tag or digest. A local image name exists only on the workstation unless it is published to a registry accessible to the nodes.

### 17. Why are immutable tags or digests preferable?

Reusing a tag makes the deployed artifact ambiguous and can interact unexpectedly with image-pull caching. An immutable tag and recorded digest make releases auditable and reproducible; digest pinning identifies the exact content.

## Kubernetes workload and networking

### 18. Why recreate the ConfigMap and Secret in EKS?

Docker Desktop Kubernetes and EKS are separate clusters. Their API objects are not synchronized, and both ConfigMaps and Secrets are namespace-scoped.

### 19. What happens if a required ConfigMap key is missing?

With a non-optional `configMapKeyRef`, the container cannot start successfully. Pod events report the missing object or key.

### 20. What does the Deployment provide?

It declares the desired replica count and Pod template. Its controller creates ReplicaSets and continuously reconciles the running Pods toward that desired state, including controlled rollouts.

### 21. What is the difference between `port`, `targetPort`, and `nodePort`?

`port` is the Service port, `targetPort` is the destination port on the selected Pod, and `nodePort` is the port exposed on cluster nodes for a NodePort Service. Here the path was assigned NodePort → Service port 80 → Pod port 5000.

### 22. How does a Service find Pods?

Its label selector matches Pod labels. The control plane maintains endpoints for matching Ready Pods, and cluster networking routes Service traffic to those endpoints.

### 23. Why can a Service have no endpoints?

The selector may not match, the Pods may not be Ready, or the Pods may be in another namespace. Comparing Service selectors with Pod labels is the first check.

### 24. Why was a security-group rule required for NodePort?

Kubernetes exposed the port on the node, but the EC2 security group still controlled inbound traffic at the AWS network boundary. Both Kubernetes routing and AWS ingress permission had to allow the request.

### 25. Why is NodePort not the preferred production exposure method?

It exposes a high port on workers and leaves load balancing, TLS, health checks, DNS, and access control largely to the operator. An ingress or AWS load balancer provides a more controlled entry point.

### 26. How would you debug an unreachable application?

Work inside out: verify container logs and Pod readiness, check Service selectors and endpoints, test with port-forwarding, then verify the NodePort, worker IP, routes, security groups, and client network.

## Operations and cost

### 27. What are the main EKS cost drivers in this lab?

The EKS control plane, EC2 worker instances, EBS volumes, public IPv4 addresses where charged, network transfer, CloudWatch usage, and retained ECR storage can all contribute. NAT gateways and load balancers would add significant hourly costs if created.

### 28. Why is deleting Pods not enough to stop EKS costs?

Pods are Kubernetes workload objects. The EKS control plane, EC2 nodes, storage, and networking resources continue to exist and can continue billing.

### 29. How did you verify cleanup?

The cluster list, running EC2 instances, active EKS CloudFormation stacks, Auto Scaling groups, load balancers, NAT gateways, and storage were checked in `us-east-1`. ECR was intentionally retained.

### 30. Summarize the project as an interview answer.

I provisioned an Amazon EKS cluster with `eksctl`, using a two-node managed EC2 node group in `us-east-1`. When the first node-group attempt failed, I traced the issue through CloudFormation events and corrected the lab configuration from `t3.medium` to `t3.small`. I then diagnosed an ARM64/AMD64 image mismatch caused by building on Apple Silicon, rebuilt the Flask image for `linux/amd64` with Docker Buildx, and pushed it to ECR. I recreated namespace-scoped configuration, deployed two replicas, exposed them through a NodePort Service and a narrowly scoped worker security-group rule, verified the application in a browser, and deleted the cluster after validating cleanup to control cost.

