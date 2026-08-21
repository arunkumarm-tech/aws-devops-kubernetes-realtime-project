# Architecture

## Delivery path

```text
Developer on macOS
  │ git push main
  ▼
GitHub repository
  │ Jenkins Pipeline script from SCM
  ▼
Local Jenkins
  ├─ checkout exact commit
  ├─ Docker buildx: linux/amd64
  ├─ AWS Credentials binding
  ├─ ECR login/tag/push
  ├─ workspace-local kubeconfig
  └─ kubectl set image + rollout + verification
        │
        ▼
Amazon ECR ───── image build-N ─────► Amazon EKS
                                          │
                                Deployment / ReplicaSet
                                          │
                                     2 Flask Pods
                                          │
                             NodePort Service :30094
                                          │
                              EC2 security-group rule
                                          │
                                     curl /health
```

## Kubernetes runtime

```text
Namespace: arun-devops
├── ConfigMap: arun-flask-config
├── Secret: arun-flask-secret
├── Deployment: arun-flask-deployment
│   └── 2 replicas, container port 5000
└── Service: arun-flask-service
    └── NodePort 30094 → port 80 → targetPort 5000
```

## EKS foundation

- Public EKS endpoint
- Two public `t3.small` Amazon Linux 2023 AMD64 workers
- No NAT Gateway
- VPC CNI (`aws-node`) for pod VPC networking
- `kube-proxy` for Service forwarding
- CoreDNS for service discovery

## Trust boundaries

- GitHub supplied versioned code and pipeline definition.
- Jenkins stored AWS secrets and exposed them only inside `withCredentials` blocks.
- AWS CLI issued the ECR token and EKS authentication material.
- A workspace-local kubeconfig separated automation context from the developer's kubeconfig.
- ECR stored immutable build tags; Kubernetes referenced the exact Jenkins build tag.
