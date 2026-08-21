# Commands Reference

This index groups the commands recorded during Day 10. See the chapter files for purpose, output, and context.

## Git and inspection

```bash
git status
git pull origin main
git diff Jenkinsfile
git add Jenkinsfile
git commit -m "<focused change>"
git push origin main
cat Jenkinsfile
tail -n 40 Jenkinsfile
tail -n 50 Jenkinsfile
tail -n 60 Jenkinsfile
sed -n '18,35p' Jenkinsfile
```

## Local tools and Docker

```bash
which docker
which aws
which kubectl
docker build -f docker/Dockerfile -t arun-jenkins-flask-app:day10-local .
docker run --rm -d --name arun-day10-local -p 5000:5000 arun-jenkins-flask-app:day10-local
curl http://localhost:5000
curl http://localhost:5000/health
docker stop arun-day10-local
docker images | grep build-3
docker buildx build --platform linux/amd64 -f docker/Dockerfile -t IMAGE:TAG --load .
```

## AWS and ECR

```bash
aws sts get-caller-identity
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin REGISTRY
docker tag LOCAL_IMAGE:TAG REGISTRY/REPOSITORY:TAG
docker push REGISTRY/REPOSITORY:TAG
aws ecr describe-images --repository-name arun-jenkins-flask-app --image-ids imageTag=build-8 --region us-east-1 \
  --query 'imageDetails[0].{Tag:imageTags[0],Digest:imageDigest,PushedAt:imagePushedAt,SizeBytes:imageSizeInBytes}' --output table
```

## EKS creation and recovery

```bash
aws eks list-clusters --region us-east-1
cat eks/eks-cluster.yaml
eksctl create cluster -f eks/eks-cluster.yaml --dry-run
eksctl create cluster -f eks/eks-cluster.yaml
aws cloudformation describe-stacks --stack-name eksctl-arun-eks-cluster-cluster --region us-east-1 \
  --query 'Stacks[0].StackStatus' --output text
aws eks list-nodegroups --cluster-name arun-eks-cluster --region us-east-1
eksctl create nodegroup --config-file eks/eks-cluster.yaml
aws eks update-kubeconfig --name arun-eks-cluster --region us-east-1
kubectl get nodes -o wide
kubectl get pods -n kube-system -o wide
aws eks list-addons --cluster-name arun-eks-cluster --region us-east-1
aws eks create-addon --cluster-name arun-eks-cluster --addon-name vpc-cni --region us-east-1
aws eks create-addon --cluster-name arun-eks-cluster --addon-name kube-proxy --region us-east-1
aws eks create-addon --cluster-name arun-eks-cluster --addon-name coredns --region us-east-1
```

## Application and deployment

```bash
kubectl create namespace arun-devops
kubectl create configmap arun-flask-config --from-literal=APP_ENV=development \
  --from-literal=APP_MESSAGE="Running from Amazon EKS ConfigMap" -n arun-devops
kubectl create secret generic arun-flask-secret --from-literal=DB_USERNAME=admin \
  --from-literal=DB_PASSWORD='<your-lab-password>' -n arun-devops
kubectl get configmap,secret -n arun-devops
kubectl apply -f kubernetes/flask-deployment.yaml
kubectl get pods -n arun-devops -o wide
kubectl set image deployment/arun-flask-deployment arun-flask-container=REGISTRY/REPO:TAG -n arun-devops
kubectl rollout status deployment/arun-flask-deployment -n arun-devops --timeout=180s
kubectl describe pod POD_NAME -n arun-devops
kubectl apply -f kubernetes/flask-service.yaml
kubectl get service arun-flask-service -n arun-devops -o wide
kubectl get endpoints arun-flask-service -n arun-devops
```

## External access and cleanup

```bash
aws ec2 authorize-security-group-ingress --group-id SECURITY_GROUP --protocol tcp --port 30094 \
  --cidr 0.0.0.0/0 --region us-east-1
curl http://NODE_PUBLIC_IP:30094
curl http://NODE_PUBLIC_IP:30094/health
eksctl delete cluster --name arun-eks-cluster --region us-east-1
```

The complete post-delete verification commands are preserved in [09-Cleanup-and-Cost-Control.md](09-Cleanup-and-Cost-Control.md).
