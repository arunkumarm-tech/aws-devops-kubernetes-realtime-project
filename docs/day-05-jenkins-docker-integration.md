Day 5 - Jenkins and Docker Integration
AWS DevOps Kubernetes Real-Time Project | Complete End-to-End Documentation

Document Purpose
This document records the complete Day 5 hands-on implementation. It is written so the same activity can be repeated later without assistance. It includes the practical steps, commands, integration flow, troubleshooting, verification, interview preparation, resume points, and GitHub update steps.
1. Objective
The objective of Day 5 is to integrate Jenkins with Docker so Jenkins can automatically build Docker images from source code stored in GitHub. After the Docker image is created, the image is run as a Docker container and the Flask application is verified through browser and curl commands.
2. Architecture Overview
GitHub Repository
        |
        v
Jenkins Freestyle Job
        |
        v
Jenkins Workspace
        |
        v
Docker Build using docker/Dockerfile
        |
        v
Docker Image: arun-jenkins-flask-app:v1
        |
        v
Docker Container: arun-jenkins-app
        |
        v
Flask Application on http://localhost:5002
Day 5 connects the components that were created in previous days: GitHub, Jenkins, Docker, Dockerfile, Flask application, and local container execution.
3. How Git, Jenkins, Docker, and Flask Are Integrated
Component	Role in Day 5	How It Connects
GitHub	Stores source code and project files	Jenkins pulls the latest code from the GitHub repository
Jenkins	Automation engine / CI tool	Runs the freestyle job and executes shell commands
Jenkins Workspace	Temporary build directory	Source code is checked out here before build commands run
Dockerfile	Image build instructions	Jenkins calls Docker build using docker/Dockerfile
Docker	Container platform	Builds the image and runs the container
Flask App	Application workload	Runs inside the Docker container on port 5000
MacBook Localhost	Test access point	Host port 5002 maps to container port 5000

4. Prerequisites
Docker Desktop installed and running on MacBook.
Jenkins LTS installed and running at http://localhost:8080.
Java 17 configured for Jenkins.
GitHub repository already connected to Jenkins.
Existing Jenkins freestyle job: arun-flask-build.
Repository branch configured as main.
Project contains application/app.py, application/requirements.txt, and docker/Dockerfile.
5. Step-by-Step Activities Performed
Step 1: Verified Docker, Java, and Jenkins Status
Purpose: Before integrating Jenkins with Docker, we verified whether Docker, Java, and Jenkins were available.
docker --version

docker ps

java -version

brew services list | grep jenkins
Observation: Docker CLI existed, but Docker daemon initially was not running. Java 17 and Jenkins service were available.
Step 2: Started Docker Desktop
Purpose: Docker commands require Docker Desktop / Docker daemon to be running.
open -a Docker
sleep 20
docker ps
Result: Docker daemon started successfully. docker ps returned an empty container list, meaning Docker was running but no containers were active.
Step 3: Opened Jenkins Dashboard
Purpose: Jenkins must be accessible before configuring build steps.
open http://localhost:8080
Result: Jenkins dashboard opened successfully. Existing job arun-flask-build was healthy and accessible.
Step 4: Verified Jenkins Can Execute Docker Commands
Purpose: Day 5 goal is Jenkins + Docker integration. Before building images, Jenkins must be able to run Docker commands.
Initial Jenkins shell commands configured inside the Jenkins job:
echo "Jenkins User:"
whoami

echo "Current Directory:"
pwd

echo "Docker Version:"
docker --version

echo "Docker Information:"
docker info

echo "Docker Images:"
docker images
Result: The build failed because Jenkins could not find the docker command.
docker: command not found
Step 5: Identified Docker Binary Path on MacBook
Purpose: Jenkins service did not inherit the same PATH as the normal terminal. We needed the full Docker binary path.
which docker
Output:
/usr/local/bin/docker
Step 6: Updated Jenkins Build Step with Full Docker Path
Purpose: Instead of relying on PATH, Jenkins was configured to call Docker using the full path.
echo "Jenkins User:"
whoami

echo "Current Directory:"
pwd

echo "Docker Path:"
which docker || true

echo "Docker Version:"
/usr/local/bin/docker --version

echo "Docker Images:"
/usr/local/bin/docker images
Result: Jenkins successfully executed Docker commands and listed Docker images. This proved Jenkins could access Docker using /usr/local/bin/docker.
Step 7: Configured Jenkins to Build Docker Image
Purpose: Jenkins now needed to build a Docker image from the repository Dockerfile.
echo "Jenkins Docker Build Started"

echo "Current User:"
whoami

echo "Workspace:"
pwd

echo "Listing project files:"
ls -la

echo "Building Docker Image from Jenkins:"
/usr/local/bin/docker build -t arun-jenkins-flask-app:v1 -f docker/Dockerfile .

echo "Verifying Docker Image:"
/usr/local/bin/docker images | grep arun-jenkins-flask-app

echo "Jenkins Docker Build Completed"
Result: The build failed with a Docker credential helper error.
docker-credential-desktop: executable file not found in $PATH
Step 8: Fixed Docker Credential Helper PATH Issue
Purpose: Docker Desktop uses helper binaries such as docker-credential-desktop. Jenkins needed Docker Desktop resource paths added to PATH.
export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"
Final Jenkins shell build script:
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
Result: Jenkins successfully built the Docker image.
Step 9: Docker Image Build Output
Important Jenkins build output confirmed the following:
Jenkins ran as user arunkumarm.
Workspace path was /Users/arunkumarm/.jenkins/workspace/arun-flask-build.
Docker version was 29.2.1.
docker-credential-desktop was found.
Dockerfile was read from docker/Dockerfile.
Base image python:3.12-slim was downloaded.
Flask dependency flask==3.0.3 was installed.
Application file application/app.py was copied.
Docker image arun-jenkins-flask-app:v1 was created.
arun-jenkins-flask-app:v1    89286207fdcc    223MB    48.4MB
Step 10: Verified Docker Image in Terminal
Purpose: Confirm that the image built by Jenkins exists in local Docker images.
docker images | grep arun-jenkins-flask-app
Output confirmed:
arun-jenkins-flask-app:v1    89286207fdcc    223MB    48.4MB
Step 11: Started Container from Jenkins-Built Image
Purpose: A Docker image is only a package. To verify the application, we must run a container from that image.
docker run -d --name arun-jenkins-app -p 5002:5000 arun-jenkins-flask-app:v1
Output returned a container ID, confirming the container started.
19c955bbca7bbbe86a9d0434d7482eecb67e9b23b1f3df89b721b78532ec34b8
Step 12: Verified Running Container
Purpose: Confirm the container is running and mapped correctly.
docker ps | grep arun-jenkins-app
Output confirmed:
19c955bbca7b   arun-jenkins-flask-app:v1   "python app.py"   Up   0.0.0.0:5002->5000/tcp   arun-jenkins-app
Step 13: Opened Application in Browser
Purpose: Verify the Flask application from the browser.
open http://localhost:5002
Important note: Browser URLs should not be typed directly in the terminal without the open command.
Step 14: Verified Application Using curl
Purpose: Validate application response from terminal.
curl http://localhost:5002
Output:
{"hostname":"19c955bbca7b","message":"Welcome to Arun's AWS DevOps Kubernetes Real-Time Project","status":"Application running successfully"}
Step 15: Verified Health Endpoint
Purpose: Validate application health endpoint.
curl http://localhost:5002/health
Output:
{"status":"healthy"}
6. Commands Used - Complete List
docker --version

docker ps

java -version

brew services list | grep jenkins

open -a Docker

open http://localhost:8080

which docker

/usr/local/bin/docker --version

/usr/local/bin/docker images

export PATH="/usr/local/bin:/opt/homebrew/bin:/Applications/Docker.app/Contents/Resources/bin:$PATH"

docker build -t arun-jenkins-flask-app:v1 -f docker/Dockerfile .

docker images | grep arun-jenkins-flask-app

docker run -d --name arun-jenkins-app -p 5002:5000 arun-jenkins-flask-app:v1

docker ps | grep arun-jenkins-app

open http://localhost:5002

curl http://localhost:5002

curl http://localhost:5002/health
7. Important Paths and Configuration Details
Item	Value	Purpose
Jenkins URL	http://localhost:8080	Access Jenkins dashboard
Jenkins Job	arun-flask-build	Freestyle job used for GitHub and Docker build
Jenkins Workspace	/Users/arunkumarm/.jenkins/workspace/arun-flask-build	Location where Jenkins checks out GitHub code
Docker Binary	/usr/local/bin/docker	Full Docker CLI path used inside Jenkins
Docker Desktop Path	/Applications/Docker.app/Contents/Resources/bin	Required for docker-credential-desktop
Dockerfile	docker/Dockerfile	Instructions to build Docker image
Application Code	application/app.py	Flask application source code
Dependencies	application/requirements.txt	Python dependency list containing flask==3.0.3
Built Image	arun-jenkins-flask-app:v1	Docker image created by Jenkins
Running Container	arun-jenkins-app	Container started from Jenkins-built image
Port Mapping	5002:5000	Host port 5002 mapped to container port 5000

8. What Happened Internally
1.GitHub Checkout: Jenkins connected to the GitHub repository and checked out the main branch into the Jenkins workspace.
2.Workspace Preparation: Jenkins stored the repository files under /Users/arunkumarm/.jenkins/workspace/arun-flask-build.
3.Dockerfile Discovery: Jenkins executed docker build using docker/Dockerfile.
4.Base Image Pull: Docker pulled python:3.12-slim from Docker Hub.
5.Dependency Installation: Docker installed Flask dependencies from application/requirements.txt.
6.Application Copy: Docker copied application/app.py into the image.
7.Image Creation: Docker created arun-jenkins-flask-app:v1.
8.Image Verification: docker images confirmed the image existed locally.
9.Container Run: The image was started as container arun-jenkins-app.
10.Application Verification: curl and browser requests confirmed the application and health endpoint were working.
9. Troubleshooting Scenarios
Scenario	Error / Symptom	Root Cause	Fix
Docker daemon not running	failed to connect to the docker API	Docker Desktop was not running	Start Docker Desktop using open -a Docker
URL typed in terminal	zsh: no such file or directory	URL was entered as a shell command	Use open http://localhost:5002 or paste URL in browser
Jenkins cannot find Docker	docker: command not found	Jenkins PATH did not include Docker CLI	Use full path /usr/local/bin/docker
Docker credential helper missing	docker-credential-desktop: executable file not found in PATH	Jenkins PATH did not include Docker Desktop resource binaries	Export PATH with /Applications/Docker.app/Contents/Resources/bin

10. Verification Checklist
Verification	Command / Location	Expected Result
Docker daemon	docker ps	No API connection error
Jenkins service	brew services list | grep jenkins	jenkins-lts started
Docker binary path	which docker	/usr/local/bin/docker
Jenkins Docker access	Jenkins Console Output	Docker version displayed
Docker image	docker images | grep arun-jenkins-flask-app	arun-jenkins-flask-app:v1
Running container	docker ps | grep arun-jenkins-app	Container Up with 5002->5000
Application home	curl http://localhost:5002	Application JSON response
Health endpoint	curl http://localhost:5002/health	{"status":"healthy"}

11. Real-Time Use Case
In real DevOps projects, developers push code to GitHub. Jenkins detects or manually triggers a build, checks out the code, runs tests, builds a Docker image, stores the image in a registry such as AWS ECR, and later deploys it to Kubernetes or EKS. Day 5 completed the GitHub to Jenkins to Docker image part of this pipeline.
Current completed Day 5 flow:
GitHub -> Jenkins -> Docker Image -> Docker Container -> Flask Application

Next Day 6 flow:
GitHub -> Jenkins -> Docker Image -> AWS ECR
12. Interview Explanation
In Day 5, I integrated Jenkins with Docker. Jenkins pulled the application source code from GitHub into its workspace and executed Docker commands to build a Docker image using the project Dockerfile. During the integration, Jenkins initially could not find the Docker command because the Jenkins runtime environment did not have the same PATH as my terminal. I identified the Docker binary path using which docker and configured Jenkins to use /usr/local/bin/docker. Later, Docker build failed because docker-credential-desktop was not available in Jenkins PATH. I resolved it by adding Docker Desktop resource binaries to PATH. After fixing these issues, Jenkins successfully built the Docker image arun-jenkins-flask-app:v1. I then ran a container named arun-jenkins-app from the image, mapped host port 5002 to container port 5000, and verified the Flask application and health endpoint successfully.
13. Interview Questions and Answers
Q: Why integrate Jenkins with Docker?
A: To automate Docker image creation as part of CI/CD. Jenkins can build images whenever code changes, reducing manual work and improving consistency.
Q: What was the Day 5 integration flow?
A: GitHub -> Jenkins -> Docker Build -> Docker Image -> Docker Container -> Flask Application.
Q: What is Jenkins workspace?
A: It is the directory where Jenkins checks out source code and runs build commands. In this project it was /Users/arunkumarm/.jenkins/workspace/arun-flask-build.
Q: Why did Jenkins fail with docker: command not found?
A: Jenkins did not have Docker CLI location in its PATH. The normal terminal knew docker, but the Jenkins service shell did not.
Q: How did you fix docker: command not found?
A: I found Docker using which docker and used the full path /usr/local/bin/docker in Jenkins shell commands.
Q: What caused docker-credential-desktop error?
A: Docker Desktop credential helper was not available in Jenkins PATH.
Q: How did you fix docker-credential-desktop error?
A: I exported PATH with /usr/local/bin, /opt/homebrew/bin, and /Applications/Docker.app/Contents/Resources/bin.
Q: What is a Dockerfile?
A: A Dockerfile contains the instructions to build a Docker image, including base image, working directory, copying files, installing dependencies, exposing ports, and startup command.
Q: Which Dockerfile was used?
A: docker/Dockerfile.
Q: What image did Jenkins build?
A: arun-jenkins-flask-app:v1.
Q: What container was started?
A: arun-jenkins-app.
Q: What port mapping was used?
A: Host port 5002 was mapped to container port 5000.
Q: How did you verify the application?
A: I opened http://localhost:5002 and used curl http://localhost:5002 and curl http://localhost:5002/health.
Q: What is the health check output?
A: {"status":"healthy"}.
Q: Does Jenkins push changes to GitHub automatically?
A: No. Jenkins reads code from GitHub and performs builds. It only pushes to GitHub if specifically configured to do so.
Q: Where is the Docker image stored after Jenkins build?
A: It is stored in the local Docker image repository on the MacBook.
Q: What is the difference between Docker image and container?
A: An image is a packaged template. A container is a running instance of that image.
Q: Why is this important in CI/CD?
A: It automates the build stage and prepares the application for deployment to registries and Kubernetes.
Q: What is the next step after Day 5?
A: Day 6 will push the Jenkins-built Docker image to AWS ECR.
Q: How would you explain this as real-time experience?
A: I built a CI workflow where Jenkins checks out code from GitHub, builds a Docker image using a Dockerfile, resolves environment issues, runs the image as a container, and validates the application endpoint.
14. Resume Points
Integrated Jenkins with Docker for automated image builds.
Configured Jenkins to execute Docker commands on macOS.
Resolved Jenkins PATH and Docker credential helper issues.
Automated Docker image creation using Jenkins freestyle jobs.
Built Docker image from GitHub source code using Jenkins.
Started and validated containerized Flask application from Jenkins-built image.
Verified application health endpoint and local container deployment.
15. GitHub Documentation Commands
Use these commands after creating docs/day-05-jenkins-docker.md in the repository:
cd ~/Projects/aws-devops-kubernetes-realtime-project

git add docs/day-05-jenkins-docker.md

git commit -m "Day 5: Add Jenkins Docker integration documentation"

git push origin main

git status
16. Day 5 Completion Status
GitHub -> Jenkins -> Docker Image -> Docker Container -> Flask Application
Status: SUCCESS
Day 5 practical implementation was completed successfully. Jenkins built the Docker image, the image was verified, a container was started from the image, and the Flask application health endpoint returned healthy status.