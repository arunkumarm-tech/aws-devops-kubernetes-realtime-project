# Day 6 — Jenkins CI Pipeline with Docker and Amazon ECR

## Project

**AWS DevOps Kubernetes Real-Time Project**

## Objective

The objective of Day 6 was to integrate Jenkins, Docker, and Amazon Elastic Container Registry (Amazon ECR). By the end of this session, Jenkins was able to build the Flask application Docker image and push it to Amazon ECR automatically.

## Architecture

```text
GitHub Repository
        |
        v
Jenkins Pipeline
        |
        v
Docker Build
        |
        v
Amazon ECR
```

## What Was Completed

- Verified AWS CLI installation and AWS authentication.
- Verified Docker installation and Docker daemon access.
- Verified Jenkins functionality.
- Created an Amazon ECR repository.
- Authenticated Docker with Amazon ECR.
- Built, tagged, and pushed the Flask Docker image.
- Integrated Jenkins with Amazon ECR.
- Configured Jenkins to build and push Docker images automatically.
- Verified the pushed images in the AWS Console.

## Tools Used

| Tool | Purpose |
|---|---|
| GitHub | Stores application source code |
| Jenkins | Automates the CI pipeline |
| Docker | Packages the application into a container image |
| Amazon ECR | Stores Docker images securely in AWS |
| AWS CLI | Authenticates and communicates with AWS |

## Step 1 — Verify AWS CLI and AWS Authentication

```bash
aws --version
aws sts get-caller-identity
```

`aws --version` confirms that AWS CLI is installed. `aws sts get-caller-identity` confirms that AWS credentials are configured and identifies the active AWS account and IAM identity.

## Step 2 — Verify Docker

```bash
docker --version
docker ps
```

These commands confirm that Docker is installed, the Docker daemon is running, and the current user can access it.

## Step 3 — Create an Amazon ECR Repository

```bash
aws ecr create-repository \
  --repository-name arun-jenkins-flask-app \
  --region <AWS_REGION>
```

This creates the private ECR repository that stores the Docker images.

## Step 4 — Authenticate Docker with Amazon ECR

```bash
aws ecr get-login-password --region <AWS_REGION> \
  | docker login \
  --username AWS \
  --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com
```

Amazon ECR is private by default. Docker must authenticate with a temporary AWS-generated token before it can push an image.

## Step 5 — Build the Docker Image

```bash
docker build \
  -t arun-jenkins-flask-app:v1 \
  -f docker/Dockerfile \
  .
```

| Option | Meaning |
|---|---|
| `docker build` | Builds a Docker image |
| `-t` | Assigns an image name and tag |
| `arun-jenkins-flask-app:v1` | Local Docker image name and version |
| `-f docker/Dockerfile` | Specifies the Dockerfile location |
| `.` | Uses the current directory as the build context |

## Step 6 — Tag the Image for Amazon ECR

```bash
docker tag arun-jenkins-flask-app:v1 \
  <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/arun-jenkins-flask-app:day6

docker tag arun-jenkins-flask-app:v1 \
  <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/arun-jenkins-flask-app:jenkins-day6
```

The full ECR repository URI tells Docker where the image must be pushed.

| Tag | Purpose |
|---|---|
| `day6` | Identifies the Day 6 milestone |
| `jenkins-day6` | Identifies the image built through Jenkins |

## Step 7 — Push the Image to Amazon ECR

```bash
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/arun-jenkins-flask-app:day6
docker push <AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com/arun-jenkins-flask-app:jenkins-day6
```

This uploads the Docker image layers to Amazon ECR. The same image can later be pulled by Kubernetes or Amazon EKS.

## Jenkins Pipeline Flow

```text
1. Jenkins pulls source code from GitHub.
2. Jenkins builds the Docker image.
3. Jenkins authenticates with Amazon ECR.
4. Jenkins tags the Docker image.
5. Jenkins pushes the image to Amazon ECR.
6. The image is verified in the AWS Console.
```

## Sample Jenkins Pipeline

> Replace `<AWS_REGION>` and `<AWS_ACCOUNT_ID>` before using this pipeline.

```groovy
pipeline {
    agent any

    environment {
        // AWS region where the ECR repository exists
        AWS_REGION = '<AWS_REGION>'
        // Amazon ECR repository name
        ECR_REPOSITORY = 'arun-jenkins-flask-app'
        // Full Amazon ECR registry address
        ECR_REGISTRY = '<AWS_ACCOUNT_ID>.dkr.ecr.<AWS_REGION>.amazonaws.com'
        // Docker image version created by Jenkins
        IMAGE_TAG = 'jenkins-day6'
        // Full Docker image name for the ECR push
        IMAGE_NAME = "${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
    }

    stages {
        stage('Verify Environment') {
            steps {
                sh '''
                    # Confirm AWS CLI access from Jenkins
                    aws --version
                    # Confirm Docker access from Jenkins
                    docker --version
                    # Confirm active AWS identity
                    aws sts get-caller-identity
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    # Build the Flask application image
                    docker build -t arun-jenkins-flask-app:v1 -f docker/Dockerfile .
                '''
            }
        }

        stage('Authenticate with Amazon ECR') {
            steps {
                sh '''
                    # Authenticate Docker using a temporary ECR password
                    aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}
                '''
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh '''
                    # Tag the local Docker image with the ECR repository URI
                    docker tag arun-jenkins-flask-app:v1 ${IMAGE_NAME}
                '''
            }
        }

        stage('Push Image to Amazon ECR') {
            steps {
                sh '''
                    # Push the tagged Docker image to Amazon ECR
                    docker push ${IMAGE_NAME}
                '''
            }
        }
    }

    post {
        success { echo 'Docker image was built and pushed to Amazon ECR successfully.' }
        failure { echo 'Pipeline failed. Review Jenkins console output for details.' }
    }
}
```

## Comments Used in the Pipeline

| Comment | Reason |
|---|---|
| `Confirm AWS CLI access from Jenkins` | Validates that Jenkins can communicate with AWS. |
| `Confirm Docker access from Jenkins` | Validates that Jenkins can build and push Docker images. |
| `Confirm active AWS identity` | Helps troubleshoot missing or incorrect AWS credentials. |
| `Build the Flask application image` | Explains the purpose of the Docker build stage. |
| `Authenticate Docker using a temporary ECR password` | Explains the secure ECR login process. |
| `Tag the local Docker image with the ECR repository URI` | Explains why image tagging is required. |
| `Push the tagged Docker image to Amazon ECR` | Explains the final image delivery step. |

Comments improve readability and help other developers understand the purpose of every Jenkins stage.

## Troubleshooting

### Docker credential helper error during Jenkins build

The Docker build initially failed because the Jenkins environment could not access a Docker credential helper configured for the local desktop environment.

### Troubleshooting Approach

1. Checked Jenkins console output.
2. Identified the Docker credential-related error.
3. Verified Docker and AWS CLI access in Jenkins.
4. Reviewed the Docker environment configuration.
5. Re-ran the pipeline after correcting the environment.

### Key Learning

A Docker configuration that works in a local terminal may not work in a Jenkins runtime. Jenkins console output should always be reviewed carefully to identify the failing stage.

## Production Best Practices

- Store AWS credentials in Jenkins Credentials, not in source code.
- Use IAM users or IAM roles instead of the AWS root account.
- Use unique image tags such as build numbers or Git commit hashes.
- Enable Amazon ECR image scanning for vulnerabilities.
- Configure ECR lifecycle policies to remove old images automatically.
- Use least-privilege IAM permissions.
- Keep the ECR repository because it will be used later for Kubernetes or Amazon EKS deployments.

## Interview Questions and Answers

### What is Amazon ECR?

Amazon ECR is a fully managed AWS container image registry used to store, manage, and deploy Docker images securely.

### Why is Amazon ECR used in a DevOps pipeline?

ECR stores versioned Docker images after a CI build. Kubernetes, ECS, or EKS can pull the same tested image for deployment.

### Why is Docker login required for ECR?

Amazon ECR is private by default. Docker login authenticates Docker with a temporary AWS-generated token before image push or pull operations.

### Why do we tag Docker images?

Tags identify image versions. They make deployments traceable and allow teams to roll back to a previously working version.

### What is the purpose of Jenkins in this project?

Jenkins automates the process of building, tagging, and pushing Docker images after changes are made to the application code.

### How do you secure AWS credentials in Jenkins?

Use Jenkins Credentials, IAM roles, secret management tools, and least-privilege IAM policies. Never hardcode access keys in source code.

### What happens after Jenkins pushes an image to ECR?

A platform such as Kubernetes, ECS, or Amazon EKS can pull the image from ECR and run the application.

### What is an ECR lifecycle policy?

An ECR lifecycle policy automatically removes old images based on rules such as image age, image count, or tag patterns.

### How would you roll back a failed deployment?

Deploy a previously tested Docker image tag, such as an earlier build number or Git commit tag.

### What was the main outcome of Day 6?

The main outcome was an automated CI workflow where Jenkins built a Docker image and pushed it to Amazon ECR.

## Resume Points

- Built a Jenkins CI pipeline to automate Docker image build and push operations.
- Integrated Jenkins with Amazon Elastic Container Registry using AWS CLI and Docker authentication.
- Created and managed Docker image tags for version tracking.
- Troubleshot Docker credential configuration issues in Jenkins.
- Applied DevOps practices including secure credential handling, image versioning, ECR scanning, and lifecycle management.
- Implemented a CI delivery workflow using GitHub, Jenkins, Docker, and Amazon ECR.

## Day 6 Completion Checklist

- [x] AWS CLI verified
- [x] AWS authentication verified
- [x] Docker verified
- [x] Jenkins verified
- [x] ECR repository created
- [x] Docker authenticated with ECR
- [x] Docker image built
- [x] Docker image tagged
- [x] Docker image pushed manually
- [x] Jenkins integrated with ECR
- [x] Jenkins automatically built and pushed the image
- [x] Docker images verified in AWS Console
- [x] Day 6 documentation completed

## Final Outcome

Day 6 transformed the CI workflow from:

```text
GitHub → Jenkins → Docker Build
```

to:

```text
GitHub → Jenkins → Docker Build → Amazon ECR
```

This completed a production-style container image delivery workflow and prepared the application image for future Kubernetes deployment.
