# Day 3 - Advanced Docker Operations and AWS ECR Integration

## 1. Objective
Learn advanced Docker operations and integrate Docker with AWS ECR.

## 2. Architecture Overview
Developer MacBook -> Docker Image -> Docker Containers -> Amazon ECR -> Future EKS Deployments

## 3. Prerequisites
- Docker Desktop
- AWS CLI configured
- Existing image: arun-devops-flask-app:v1
- Running container: arun-flask-container

## 4. Step-by-Step Tasks Performed
1. Verified running containers
2. Viewed logs
3. Accessed container shell
4. Inspected container metadata
5. Verified Docker networking
6. Created Docker volume
7. Started volume-backed container
8. Tagged Docker image
9. Verified health checks
10. Verified AWS account
11. Created ECR repository
12. Logged in to ECR
13. Tagged image for ECR
14. Pushed image to ECR
15. Verified uploaded image

## 5. Commands Used

```bash
docker ps
docker logs arun-flask-container
docker exec -it arun-flask-container /bin/sh
pwd
ls -la
python --version
exit

docker inspect -f '{{.State.Status}}' arun-flask-container
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' arun-flask-container
docker inspect -f '{{.Config.Image}}' arun-flask-container
docker inspect -f '{{.HostConfig.PortBindings}}' arun-flask-container

docker network ls
docker inspect -f '{{range .NetworkSettings.Networks}}{{.NetworkID}} {{.IPAddress}} {{.Gateway}}{{end}}' arun-flask-container

docker volume create arun-flask-data
docker volume ls

docker run -d --name arun-flask-volume-demo -p 5002:5000 -v arun-flask-data:/app/data arun-devops-flask-app:v1
docker inspect arun-flask-volume-demo | grep -A 10 Mounts

docker tag arun-devops-flask-app:v1 arun-devops-flask-app:day3
docker images | grep arun-devops-flask-app
curl http://localhost:5001/health
curl http://localhost:5002/health

aws --version
aws sts get-caller-identity
aws ecr describe-repositories --repository-names arun-devops-flask-app --region us-east-1

export AWS_PAGER=""
echo 'export AWS_PAGER=""' >> ~/.zshrc
source ~/.zshrc

aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 160827082645.dkr.ecr.us-east-1.amazonaws.com

docker tag arun-devops-flask-app:day3 160827082645.dkr.ecr.us-east-1.amazonaws.com/arun-devops-flask-app:day3

docker push 160827082645.dkr.ecr.us-east-1.amazonaws.com/arun-devops-flask-app:day3

aws ecr list-images --repository-name arun-devops-flask-app --region us-east-1
```

## 6. Configuration Files
No new files were created on Day 3.

## 7. Detailed Explanation
- docker logs: View container logs.
- docker exec -it: Open an interactive shell.
- docker inspect: Retrieve detailed metadata.
- Docker volumes: Persistent storage.
- Docker networking: Internal IP and gateway.
- Amazon ECR: Private Docker registry in AWS.

## 8. Troubleshooting Scenarios
- AWS CLI pager stuck with ':' -> Press q and set AWS_PAGER="".
- Docker login expected output -> Login Succeeded.
- Root account used for learning only.

## 9. Real-Time Use Cases
CI/CD pipelines use Jenkins or GitHub Actions to build images and push them to ECR before deployment to EKS.

## 10. Interview Explanation
I used advanced Docker commands for logs, shell access, inspection, networking, and volumes. I integrated Docker with AWS ECR by authenticating, tagging, pushing, and verifying images.

## 11. Interview Questions and Answers
1. What is docker logs? Displays runtime logs.
2. What is docker exec? Runs commands inside a container.
3. What is docker inspect? Shows low-level metadata.
4. What is a Docker volume? Persistent storage.
5. What is Amazon ECR? AWS private container registry.
6. Why push images to ECR? To deploy to ECS/EKS.
7. What does docker tag do? Assigns a new version label.
8. What command verifies AWS identity? aws sts get-caller-identity.
9. What command lists ECR images? aws ecr list-images.
10. Why avoid the root account? Security best practice.

## 12. Key Learnings
- Container inspection
- Networking analysis
- Persistent storage
- Image versioning
- AWS ECR integration

## 13. Resume Points
- Implemented advanced Docker operations and troubleshooting.
- Integrated Docker with Amazon ECR.
- Pushed versioned container images to AWS.
- Documented interview-focused explanations and Q&A.

## 14. Git Commands Used

```bash
git add docs/day-03-advanced-docker-ecr.md
git commit -m "Day 3: Advanced Docker operations and AWS ECR integration"
git push origin main
git status
```
