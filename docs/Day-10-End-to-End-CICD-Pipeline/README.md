# Day 10 — End-to-End CI/CD Pipeline

Day 10 connected the complete delivery path for the AWS DevOps Kubernetes Real-Time Project:

```text
GitHub → Jenkins → Docker → Amazon ECR → Amazon EKS → NodePort → Internet
```

This is an implementation record of the real lab session, including unsuccessful attempts. It is not a clean-room tutorial. Commands, build numbers, errors, resource names, and verification results are preserved from the session. Secret values are intentionally omitted.

## Final result

- Jenkins read the pipeline from GitHub and generated immutable `build-N` tags.
- Jenkins built an AMD64 image on an Apple Silicon host, authenticated to AWS, pushed to ECR, configured an isolated kubeconfig, and rolled out the image to EKS.
- Build 12 completed the first successful automated EKS rollout.
- Build 13 added post-deployment verification and finished successfully.
- Two replicas were available, the Service used NodePort `30094`, and public `/health` returned `{"status":"healthy"}`.
- EKS and its chargeable supporting infrastructure were deleted and verified. ECR was deliberately retained temporarily for documentation.

## Contents

1. [Project and Jenkins setup](01-Project-and-Jenkins-Setup.md)
2. [Jenkinsfile and SCM](02-Jenkinsfile-and-SCM.md)
3. [Docker build and local validation](03-Docker-Build-and-Local-Validation.md)
4. [AWS credentials and ECR](04-AWS-Credentials-and-ECR.md)
5. [EKS recreation and cluster recovery](05-EKS-Recreation-and-Cluster-Recovery.md)
6. [Jenkins-to-EKS deployment](06-Jenkins-to-EKS-Deployment.md)
7. [Troubleshooting and root-cause analysis](07-Troubleshooting-and-Root-Cause-Analysis.md)
8. [External access and verification](08-External-Access-and-Verification.md)
9. [Cleanup and cost control](09-Cleanup-and-Cost-Control.md)
10. [Architecture](Architecture.md)
11. [Commands reference](Commands-Reference.md)
12. [Interview questions](Interview-Questions.md)
13. [Tips and best practices](Tips-and-Best-Practices.md)
14. [Mistakes we made](Mistakes-We-Made.md)
15. [Day 10 summary](Day-10-Summary.md)

## Recorded environment

| Item | Value |
|---|---|
| AWS region | `us-east-1` |
| AWS account | `160827082645` |
| IAM user | `arun-devops` |
| ECR repository | `arun-jenkins-flask-app` |
| EKS cluster | `arun-eks-cluster` |
| Node group | `arun-eks-ng` |
| Namespace | `arun-devops` |
| Deployment | `arun-flask-deployment` |
| Service | `arun-flask-service` |
| Jenkins job | `arun-devops-day10-cicd` |

> Historical note: public IPs, security-group IDs, image digests, and software versions below are session evidence. The cluster and related resources were deleted, so those endpoints are no longer expected to work.
