# Day 10 Summary

## Outcome

Day 10 turned the Day 9 Kubernetes application into a working CI/CD system. GitHub held the pipeline and application source. Jenkins checked out `main`, built a platform-compatible container, securely authenticated to AWS, pushed a uniquely tagged image to ECR, connected to EKS with an isolated kubeconfig, performed a rolling update, and verified the resulting workload.

The strongest final evidence was:

```text
Deployment: 2/2 available
Image: .../arun-jenkins-flask-app:build-13
Service: 80:30094/TCP
Public /health: {"status":"healthy"}
Pipeline: Finished: SUCCESS
```

The session also demonstrated real recovery work: a duplicate CloudFormation create, a control plane without a node group, missing EKS add-ons, two `NotReady` workers, a rollout timeout, `ImagePullBackOff`, an ARM64/AMD64 mismatch, and blocked NodePort traffic. Each issue was investigated from evidence and verified after the fix.

## Skills gained

- Jenkins Pipeline-as-Code and SCM integration
- Service-process PATH troubleshooting on macOS
- Jenkins credential storage and scoped AWS credential binding
- ECR authentication, tagging, push, and digest validation
- EKS/CloudFormation/node-group lifecycle diagnosis
- EKS managed add-on recovery
- Kubernetes bootstrap, rollout, pod-event, Service, and endpoint analysis
- Cross-platform container builds with buildx
- AWS security-group and public connectivity troubleshooting
- Cost-aware teardown and independent cleanup verification

## Resume-ready points

- Built an end-to-end CI/CD pipeline integrating GitHub, Jenkins, Docker, Amazon ECR, and Amazon EKS.
- Implemented traceable `build-N` container tagging, secure Jenkins AWS credential binding, ECR digest verification, and automated Kubernetes rolling deployments.
- Diagnosed and resolved Jenkins PATH issues, incomplete EKS provisioning, missing VPC CNI/CoreDNS/kube-proxy add-ons, Kubernetes `ImagePullBackOff`, and ARM64-to-AMD64 incompatibility.
- Added post-deployment checks for Deployment, Pods, and Service and validated public application and health endpoints through NodePort.
- Executed and independently verified complete teardown of EKS, EC2, CloudFormation, Auto Scaling, NAT, ELB, EBS, and Elastic IP resources.

## Final resource status

All expensive Day 10 infrastructure was removed. ECR was intentionally retained temporarily so build tags and digests remained available while this documentation was prepared; it was explicitly scheduled for separate deletion afterward.
