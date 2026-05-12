# Day 1 and Day 2 - Complete DevOps Project Notes

## Day 1 - GitHub Project Initialization

### What We Did
- Created new GitHub repository
- Cloned repository to MacBook
- Created project folder structure
- Added .gitkeep files
- Created documentation folder

### Folder Structure
- application/
- docker/
- jenkins/
- kubernetes/
- terraform/
- monitoring/
- scripts/
- docs/

### Commands Used
mkdir -p application docker jenkins kubernetes terraform monitoring scripts docs

touch application/.gitkeep docker/.gitkeep jenkins/.gitkeep kubernetes/.gitkeep terraform/.gitkeep monitoring/.gitkeep scripts/.gitkeep

git add .
git commit -m "Day 1: Initialize project structure"
git push origin main

### Why .gitkeep Was Used
Git does not track empty folders. .gitkeep is used to preserve empty folder structure in GitHub.

### Interview Explanation
I created a professional DevOps repository structure to organize application code, Docker files, Jenkins pipelines, Kubernetes manifests, Terraform infrastructure, monitoring configuration, scripts, and documentation.

### Day 1 Interview Questions

Q1. Why do we use Git?
A. Git is used for version control, collaboration, rollback, and tracking changes.

Q2. Why is folder structure important?
A. It keeps application, infrastructure, CI/CD, monitoring, and documentation files cleanly separated.

Q3. Why use .gitkeep?
A. Git does not track empty directories, so .gitkeep helps preserve folder structure.

Q4. Why keep documentation in Git?
A. It helps with knowledge sharing, troubleshooting, interview preparation, and project maintenance.

---

## Day 2 - Docker and Containerization

### What We Did
- Created Python Flask application
- Created requirements.txt
- Created Dockerfile
- Built Docker image
- Ran Docker container
- Fixed port conflict issue
- Fixed container name conflict issue
- Tested health endpoint

### Files Created

application/app.py
application/requirements.txt
docker/Dockerfile

### Dockerfile Used
FROM python:3.12-slim

WORKDIR /app

COPY application/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY application/app.py .

EXPOSE 5000

CMD ["python", "app.py"]

### Docker Commands Used
docker --version
docker ps
docker build -t arun-devops-flask-app:v1 -f docker/Dockerfile .
docker images | grep arun-devops-flask-app
docker run -d --name arun-flask-container -p 5001:5000 arun-devops-flask-app:v1
docker ps
curl http://localhost:5001/health

### Successful Output
{"status":"healthy"}

---

## Troubleshooting Scenario 1 - Port Already in Use

### Error
bind: address already in use

### Root Cause
Host port 5000 was already used by another process.

### Resolution
Used host port 5001 and mapped it to container port 5000.

Command:
docker run -d --name arun-flask-container -p 5001:5000 arun-devops-flask-app:v1

### Interview Explanation
During container deployment, the application failed because host port 5000 was already occupied. I resolved it by mapping container port 5000 to host port 5001.

---

## Troubleshooting Scenario 2 - Container Name Already Exists

### Error
Conflict. The container name "/arun-flask-container" is already in use

### Root Cause
A failed Docker run created a stale container object.

### Resolution
docker ps -a
docker rm arun-flask-container

Then reran the container successfully.

### Interview Explanation
The failed deployment left a stale container. I listed all containers, removed the stale container, and redeployed successfully.

---

## Docker Interview Questions and Answers

Q1. What is Docker?
A. Docker is a containerization platform used to package applications with dependencies.

Q2. What is a Docker image?
A. A Docker image is a read-only template used to create containers.

Q3. What is a Docker container?
A. A container is a running instance of a Docker image.

Q4. Difference between image and container?
A. Image is a blueprint. Container is the running instance.

Q5. What is Dockerfile?
A. Dockerfile contains instructions to build a Docker image.

Q6. What is FROM?
A. FROM defines the base image.

Q7. What is WORKDIR?
A. WORKDIR sets the working directory inside the container.

Q8. What is COPY?
A. COPY copies files from local machine to Docker image.

Q9. What is RUN?
A. RUN executes commands during image build.

Q10. What is CMD?
A. CMD defines the command executed when container starts.

Q11. What is EXPOSE?
A. EXPOSE documents the port used by the container.

Q12. What does -p 5001:5000 mean?
A. It maps host port 5001 to container port 5000.

Q13. What does -d mean?
A. Detached mode. Container runs in background.

Q14. How to list running containers?
A. docker ps

Q15. How to list all containers?
A. docker ps -a

Q16. How to remove a container?
A. docker rm container-name

Q17. How to check logs?
A. docker logs container-name

Q18. Why use python:3.12-slim?
A. It is lightweight and reduces image size.

Q19. Why Docker is important in DevOps?
A. Docker provides consistency, portability, faster deployment, and CI/CD support.

Q20. How did you validate the application?
A. I tested the /health endpoint using curl and received healthy status.

---

## Resume Points

- Created structured GitHub repository for AWS DevOps Kubernetes project.
- Containerized Python Flask application using Docker.
- Built and ran Docker image locally.
- Implemented health check endpoint.
- Troubleshot Docker port conflict and container name conflict.
- Documented commands, issues, resolutions, and interview scenarios.

