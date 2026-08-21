# 06 — Jenkins to EKS Deployment

## Recreate application prerequisites

The EKS cluster was new, so Day 9 namespace-scoped resources did not exist.

```bash
kubectl get namespace arun-devops
kubectl create namespace arun-devops
kubectl get namespace arun-devops

kubectl create configmap arun-flask-config \
  --from-literal=APP_ENV=development \
  --from-literal=APP_MESSAGE="Running from Amazon EKS ConfigMap" \
  -n arun-devops

kubectl create secret generic arun-flask-secret \
  --from-literal=DB_USERNAME=admin \
  --from-literal=DB_PASSWORD='<your-lab-password>' \
  -n arun-devops

kubectl get configmap,secret -n arun-devops
```

The real password is deliberately not documented.

## Prove Jenkins has kubectl

```bash
which kubectl
```

Actual: `/opt/homebrew/bin/kubectl`.

The Jenkins stage ran:

```bash
kubectl version --client
```

Build 9 returned client `v1.36.1`, pushed an ECR image with digest `sha256:f8967e...`, and finished successfully.

## Isolated kubeconfig

Jenkins used a workspace-local kubeconfig:

```bash
export KUBECONFIG="${WORKSPACE}/.kubeconfig"
aws eks update-kubeconfig \
  --name arun-eks-cluster \
  --region ${AWS_REGION} \
  --kubeconfig "${KUBECONFIG}"
kubectl get nodes
```

This prevented the pipeline from depending on or changing the user's normal `~/.kube/config`.

An intermediate mistake ran the Jenkins-only `export KUBECONFIG="${WORKSPACE}/.kubeconfig"` in a normal terminal, where `WORKSPACE` was unset. It was corrected with:

```bash
unset KUBECONFIG
echo $KUBECONFIG
```

## Establish a baseline Deployment

`kubectl set image` updates an existing Deployment; it does not create one. The fresh namespace initially returned no deployments, so the manifest was applied first:

```bash
kubectl get deployment -n arun-devops
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl get pods -n arun-devops -o wide
```

Both baseline replicas reached `Running`, one on each worker.

## Automated update

```bash
kubectl set image deployment/arun-flask-deployment \
  arun-flask-container=${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} \
  -n arun-devops

kubectl rollout status deployment/arun-flask-deployment \
  -n arun-devops \
  --timeout=180s
```

Build 11 authenticated, pushed, configured EKS access, and updated the Deployment, but timed out because its ARM64 image could not run on AMD64 nodes. After the buildx fix, build 12 completed:

```text
deployment "arun-flask-deployment" successfully rolled out
Finished: SUCCESS
```

Verification:

```bash
kubectl get pods -n arun-devops -o wide
kubectl get deployment arun-flask-deployment \
  -n arun-devops \
  -o jsonpath='{.spec.template.spec.containers[0].image}{"\n"}'
```

The deployed image was `.../arun-jenkins-flask-app:build-12`.

Build 13 added the `Verify Deployment` stage. It reported Deployment `2/2`, two new running pods, old pods terminating normally during the rolling update, and the NodePort Service. The final deployed image was `build-13`.
