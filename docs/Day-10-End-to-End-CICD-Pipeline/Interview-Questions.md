# Interview Questions

## 1. Why use Pipeline script from SCM?

It versions the delivery logic with application code, supports review and rollback, and lets Jenkins report the exact commit used by each build.

## 2. Why did Jenkins fail to find Docker although Docker worked in Terminal?

Jenkins ran as a service with a smaller environment than the interactive shell. `/usr/local/bin` was absent from its PATH.

## 3. Why use `BUILD_NUMBER` in the image tag?

It creates a traceable, immutable artifact per pipeline execution and makes rollback and audit easier than overwriting `latest`.

## 4. How were AWS secrets protected?

The AWS Credentials plugin stored them. `withCredentials` injected them only into relevant stages and masked matching console values. They were never committed.

## 5. What does ECR login do?

AWS CLI requests a short-lived registry password. It is piped to `docker login --password-stdin`, avoiding a password in the command line or Jenkinsfile.

## 6. Why did nodes remain NotReady?

The cluster creation was interrupted and no EKS add-ons were registered. Without VPC CNI, pod networking was unavailable. Installing `vpc-cni` created `aws-node` pods and the nodes became Ready.

## 7. Why install VPC CNI before CoreDNS?

Networking is foundational. CoreDNS pods need schedulable, network-ready nodes. The observed readiness change after VPC CNI confirmed the dependency.

## 8. What caused `ImagePullBackOff`?

The broad state came from a platform mismatch. Kubernetes Events said `no match for platform in manifest`; the image was ARM64 while the EKS nodes were AMD64.

## 9. Why was `--load` required with buildx?

The later pipeline stages used `docker tag` and `docker push`. `--load` placed the buildx result in the local Docker image store for those commands.

## 10. Why create the Deployment before using `kubectl set image`?

`set image` patches an existing workload; it does not create the Deployment. A baseline manifest established the object Jenkins later updated.

## 11. What happens during a rolling update?

Kubernetes creates a new ReplicaSet, starts new pods, waits for readiness and availability constraints, and then scales down the old ReplicaSet. Old pods in `Terminating` can be normal.

## 12. Why did a successful rollout not complete testing?

Rollout success proves workload availability inside Kubernetes. Service selectors, endpoints, security groups, and application behavior still require verification.

## 13. Why use a workspace-local kubeconfig?

It isolates Jenkins from the developer's personal context, avoids side effects, and makes the job's cluster access explicit.

## 14. Why did the first ECR query fail?

The table projection assumed every image detail produced two cells. Untagged or differently shaped entries violated that assumption. Querying a specific known tag produced a stable object.

## 15. How was cleanup validated?

The team queried EKS, running EC2, active CloudFormation stacks, ASGs, NAT gateways, load balancers, unattached volumes, and Elastic IPs. All were empty.
