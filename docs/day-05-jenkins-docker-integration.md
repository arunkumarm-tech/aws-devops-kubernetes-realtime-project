# Day 5 - Jenkins and Docker Integration

## 1. Objective

The objective of Day 5 is to integrate Jenkins with Docker so Jenkins can automatically build a Docker image from the Flask application source code stored in GitHub.

By the end of this session, Jenkins successfully performed the following:

- Pulled source code from GitHub.
- Accessed Docker from Jenkins.
- Built a Docker image using the project Dockerfile.
- Verified the Docker image locally.
- Started a container from the Jenkins-built image.
- Verified the Flask application and health endpoint.

---

## 2. Architecture Overview

```text
GitHub Repository
        |
        v
Jenkins Freestyle Job
        |
        v
Jenkins Workspace
        |
        v
Docker Build
        |
        v
Docker Image
        |
        v
Docker Container
        |
        v
Flask Application
```

---

## 3. How GitHub, Jenkins, Docker, and Flask Are Integrated

| Component | Role in the Project | What Happened in Day 5 |
|---|---|---|
| GitHub | Stores source code and project files | Jenkins pulled latest code from the GitHub repository |
| Jenkins | CI automation server | Jenkins triggered the build job and executed Docker commands |
| Jenkins Workspace | Local build directory used by Jenkins | GitHub code was checked out into Jenkins workspace |
| Dockerfile | Instructions to build the image | Jenkins used `docker/Dockerfile` to build the image |
| Docker | Builds and runs containers | Docker built the image and ran the container |
| Flask | Python web application | Flask app ran inside the Docker container |
| Browser / curl | Application validation | Application and health endpoint were tested successfully |

---

## 4. Prerequisites

Before starting Day 5, the following were already completed:

- GitHub repository was created.
- Flask application files were available.
- Docker Desktop was installed.
- Jenkins LTS was installed and running.
- Java 17 was configured.
- Jenkins was already integrated with GitHub from Day 4.
- Docker Desktop was started before running Docker commands.

---

## 5. Step-by-Step Activities Performed

### Step 1: Verified Docker, Java, and Jenkins

Commands used:

```bash
docker --version
docker ps
java -version
brew services list | grep jenkins
```

Purpose:

| Command | Purpose |
|---|---|
| `docker --version` | Verify Docker CLI is installed |
| `docker ps` | Verify Docker daemon is running |
| `java -version` | Verify Java 17 is available |
| `brew services list \| grep jenkins` | Verify Jenkins service is running |

Observation:

Docker CLI was available, but Docker daemon was initially not running.

Error:

```text
failed to connect to the docker API
```

Fix:

Started Docker Desktop.

---

### Step 2: Opened Jenkins Dashboard

Command used:

```bash
open http://localhost:8080
```

Purpose:

To open Jenkins in the browser and access the existing Jenkins job.

Jenkins job used:

```text
arun-flask-build
```

---

### Step 3: Verified Jenkins Docker Access

Initial Jenkins shell command:

```bash
docker --version
```

Build failed with:

```text
docker: command not found
```

Root cause:

Jenkins did not have the same `PATH` as the normal Mac terminal.

---

### Step 4: Found Docker Binary Path

Command used in Mac terminal:

```bash
which docker
```

Output:

```text
/usr/local/bin/docker
```

Meaning:

Docker CLI exists, but Jenkins was not able to find it using the default shell path.

---

### Step 5: Updated Jenkins Build Step with Full Docker Path

Jenkins shell command used:

```bash
echo "Jenkins User:"
whoami

echo "Current Directory:"
pwd

echo "Docker Version:"
/usr/local/bin/docker --version

echo "Docker Images:"
/usr/local/bin/docker images
```

Result:

Jenkins successfully executed Docker commands using the full Docker path.

---

### Step 6: Fixed Docker Credential Helper Issue

When Jenkins tried to build the Docker image, the build failed with:

```text
docker-credential-desktop: executable file not found in $PATH
```

Root cause:

Docker Desktop credential helper was not available in Jenkins shell `PATH`.

Fix:

Added Docker Desktop resource path to Jenkins shell:

```bash
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

---

### Step 7: Configured Jenkins Docker Build

Final Jenkins shell script:

```bash
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"

echo "Jenkins Docker Build Started"

echo "Current User:"
whoami

echo "Workspace:"
pwd

echo "Docker Version:"
docker --version

echo "Docker Credential Helper:"
which docker-credential-desktop || true

echo "Building Docker Image from Jenkins:"
docker build -t arun-jenkins-flask-app:v1 -f docker/Dockerfile .

echo "Verifying Docker Image:"
docker images | grep arun-jenkins-flask-app

echo "Jenkins Docker Build Completed"
```

Result:

Docker image was built successfully by Jenkins.

---

### Step 8: Verified Docker Image

Command used:

```bash
docker images | grep arun-jenkins-flask-app
```

Output:

```text
arun-jenkins-flask-app:v1
```

Image created:

```text
arun-jenkins-flask-app:v1
```

---

### Step 9: Started Container from Jenkins-Built Image

Command used:

```bash
docker run -d --name arun-jenkins-app -p 5002:5000 arun-jenkins-flask-app:v1
```

Purpose:

To start a running container from the image created by Jenkins.

Container created:

```text
arun-jenkins-app
```

Port mapping:

```text
Host Port 5002 -> Container Port 5000
```

---

### Step 10: Verified Running Container

Command used:

```bash
docker ps | grep arun-jenkins-app
```

Output confirmed:

```text
arun-jenkins-app
0.0.0.0:5002->5000/tcp
```

---

### Step 11: Verified Flask Application

Opened application in browser:

```bash
open http://localhost:5002
```

Tested using curl:

```bash
curl http://localhost:5002
curl http://localhost:5002/health
```

Successful output:

```json
{"hostname":"19c955bbca7b","message":"Welcome to Arun's AWS DevOps Kubernetes Real-Time Project","status":"Application running successfully"}
```

Health check:

```json
{"status":"healthy"}
```

---

## 6. Commands Used

```bash
docker --version
docker ps
java -version
brew services list | grep jenkins
open http://localhost:8080
which docker
docker images | grep arun-jenkins-flask-app
docker run -d --name arun-jenkins-app -p 5002:5000 arun-jenkins-flask-app:v1
docker ps | grep arun-jenkins-app
open http://localhost:5002
curl http://localhost:5002
curl http://localhost:5002/health
```

Jenkins build script:

```bash
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"

echo "Jenkins Docker Build Started"

echo "Current User:"
whoami

echo "Workspace:"
pwd

echo "Docker Version:"
docker --version

echo "Docker Credential Helper:"
which docker-credential-desktop || true

echo "Building Docker Image from Jenkins:"
docker build -t arun-jenkins-flask-app:v1 -f docker/Dockerfile .

echo "Verifying Docker Image:"
docker images | grep arun-jenkins-flask-app

echo "Jenkins Docker Build Completed"
```

---

## 7. Important Files and Paths

| Item | Path / Name | Purpose |
|---|---|---|
| Jenkins Job | `arun-flask-build` | Jenkins freestyle job used for CI build |
| Jenkins Workspace | `/Users/arunkumarm/.jenkins/workspace/arun-flask-build` | Location where Jenkins checked out GitHub code |
| Dockerfile | `docker/Dockerfile` | Docker image build instructions |
| Flask App | `application/app.py` | Python Flask application |
| Requirements File | `application/requirements.txt` | Python dependency list |
| Docker Image | `arun-jenkins-flask-app:v1` | Image built by Jenkins |
| Docker Container | `arun-jenkins-app` | Running container created from Jenkins-built image |
| Application URL | `http://localhost:5002` | Flask app access URL |
| Health URL | `http://localhost:5002/health` | Health check endpoint |

---

## 8. What Happened Internally

When Jenkins build was triggered, the following internal flow happened:

| Step | Internal Action |
|---|---|
| 1 | Jenkins connected to GitHub |
| 2 | Jenkins pulled the latest source code |
| 3 | Source code was stored inside Jenkins workspace |
| 4 | Jenkins executed shell commands |
| 5 | Docker build command was triggered |
| 6 | Docker read `docker/Dockerfile` |
| 7 | Docker pulled `python:3.12-slim` base image |
| 8 | Docker copied `requirements.txt` |
| 9 | Docker installed Flask dependency |
| 10 | Docker copied `app.py` |
| 11 | Docker created image `arun-jenkins-flask-app:v1` |
| 12 | Container was created from the image |
| 13 | Flask app was accessed on `localhost:5002` |
| 14 | Health check returned healthy status |

---

## 9. Troubleshooting Scenarios

### Scenario 1: Docker Daemon Not Running

Error:

```text
failed to connect to the docker API
```

Root cause:

Docker Desktop was not running.

Fix:

Started Docker Desktop and verified using:

```bash
docker ps
```

---

### Scenario 2: Jenkins Could Not Find Docker

Error:

```text
docker: command not found
```

Root cause:

Jenkins shell environment did not include Docker CLI path.

Fix:

Used full Docker path:

```bash
/usr/local/bin/docker
```

---

### Scenario 3: Docker Credential Helper Not Found

Error:

```text
docker-credential-desktop: executable file not found in $PATH
```

Root cause:

Docker Desktop credential helper path was missing in Jenkins shell environment.

Fix:

Added Docker Desktop binaries to Jenkins PATH:

```bash
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
```

---

### Scenario 4: URL Entered Directly in Terminal

Error:

```text
zsh: no such file or directory: http://localhost:5002
```

Root cause:

A browser URL was typed directly into terminal as if it was a command.

Fix:

Used:

```bash
open http://localhost:5002
```

or:

```bash
curl http://localhost:5002
```

---

## 10. Real-Time Use Case

In a real DevOps project, this workflow is used when a developer pushes code to GitHub.

The CI/CD flow works like this:

```text
Developer pushes code
        |
        v
GitHub stores the code
        |
        v
Jenkins pulls the latest code
        |
        v
Jenkins builds Docker image
        |
        v
Docker image is tested locally
        |
        v
Image is pushed to container registry such as AWS ECR
        |
        v
Kubernetes or EKS deploys the image
```

Day 5 completed the CI part where Jenkins builds a Docker image and validates the application locally.

---

## 11. Interview Explanation

I integrated Jenkins with Docker by configuring Jenkins to execute Docker commands from a freestyle job. Initially, Jenkins could not find the Docker command because the Jenkins shell did not inherit the same PATH as my terminal. I identified the Docker binary path using `which docker` and updated the Jenkins build step to use `/usr/local/bin/docker`.

During Docker build, I faced another issue where `docker-credential-desktop` was not found. I resolved it by adding Docker Desktop binaries to the Jenkins shell PATH. After that, Jenkins successfully built a Docker image named `arun-jenkins-flask-app:v1` using the project Dockerfile.

I then ran a container named `arun-jenkins-app` from the Jenkins-built image and verified the Flask application using browser and curl. The `/health` endpoint returned healthy status, confirming the application was running successfully.

---

## 12. Interview Questions and Answers

### Q1: Why integrate Jenkins with Docker?

Jenkins is used for CI/CD automation, and Docker is used to package applications. Integrating them allows Jenkins to automatically build Docker images whenever source code changes.

---

### Q2: What happened when Jenkins triggered the Docker build?

Jenkins pulled code from GitHub into its workspace, executed Docker build command, used the Dockerfile, installed dependencies, copied application code, and created a Docker image.

---

### Q3: Why did Jenkins fail with `docker: command not found`?

Jenkins did not have Docker CLI path in its shell environment.

---

### Q4: How did you fix `docker: command not found`?

I identified Docker path using `which docker` and used `/usr/local/bin/docker` in Jenkins build commands.

---

### Q5: What is Jenkins workspace?

Jenkins workspace is the directory where Jenkins checks out source code and runs build steps.

---

### Q6: What was the Jenkins workspace path in this project?

```text
/Users/arunkumarm/.jenkins/workspace/arun-flask-build
```

---

### Q7: What is a Dockerfile?

A Dockerfile is a file containing instructions to build a Docker image.

---

### Q8: Which Dockerfile was used?

```text
docker/Dockerfile
```

---

### Q9: What Docker image was created by Jenkins?

```text
arun-jenkins-flask-app:v1
```

---

### Q10: What container was created from the Jenkins-built image?

```text
arun-jenkins-app
```

---

### Q11: What is the difference between Docker image and Docker container?

A Docker image is a packaged template. A Docker container is a running instance of that image.

---

### Q12: Why was port `5002:5000` used?

The Flask app runs on port `5000` inside the container. It was mapped to host port `5002` so it could be accessed from the Mac browser.

---

### Q13: How did you verify the application?

Using:

```bash
curl http://localhost:5002
curl http://localhost:5002/health
```

---

### Q14: What does the `/health` endpoint confirm?

It confirms that the application is running and responding successfully.

---

### Q15: What is the next step after Jenkins builds the Docker image?

The next step is to push the Docker image to AWS ECR, which will be handled in Day 6.

---

## 13. Resume Points

- Integrated Jenkins with Docker for automated Docker image builds.
- Configured Jenkins to execute Docker commands on macOS.
- Troubleshot Jenkins Docker PATH issues.
- Resolved Docker credential helper issue in Jenkins environment.
- Automated Docker image creation using Jenkins freestyle job.
- Built and verified Flask application Docker image using Jenkins.
- Started and validated Docker container from Jenkins-built image.
- Verified application and health endpoint using browser and curl.

---

## 14. Git Commands Used

```bash
cd ~/Projects/aws-devops-kubernetes-realtime-project

git add docs/day-05-jenkins-docker-integration.md

git commit -m "Day 5: Add Jenkins Docker integration documentation"

git push origin main

git status
```

---

## 15. Day 5 Completion Status

```text
GitHub -> Jenkins -> Docker Image -> Docker Container -> Flask Application

Status: SUCCESS
```

Day 5 practical implementation is completed successfully.

