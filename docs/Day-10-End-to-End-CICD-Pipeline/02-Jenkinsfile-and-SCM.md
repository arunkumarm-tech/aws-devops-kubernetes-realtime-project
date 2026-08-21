# 02 — Jenkinsfile and SCM

## Pipeline evolution

The initial pipeline defined an image name and used Jenkins' `BUILD_NUMBER` for a unique tag:

```groovy
environment {
    IMAGE_NAME = 'arun-jenkins-flask-app'
    IMAGE_TAG  = "build-${BUILD_NUMBER}"
}
```

This produced tags such as `build-2`, `build-3`, `build-8`, `build-11`, `build-12`, and `build-13`. It gave every pipeline execution a traceable artifact instead of repeatedly overwriting `latest`.

The environment block eventually became:

```groovy
environment {
    PATH         = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
    IMAGE_NAME   = 'arun-jenkins-flask-app'
    IMAGE_TAG    = "build-${BUILD_NUMBER}"
    AWS_REGION   = 'us-east-1'
    AWS_ACCOUNT  = '160827082645'
    ECR_REPO     = 'arun-jenkins-flask-app'
    ECR_REGISTRY = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
}
```

The explicit paths were necessary because a Jenkins service does not necessarily inherit an interactive shell's PATH.

## Final stage sequence

```text
Declarative: Checkout SCM
Checkout
Docker Build
AWS CLI Check
AWS Identity Check
ECR Login
Tag Docker Image
kubectl CLI Check
Push Image to ECR
Configure EKS Access
Deploy to EKS
Verify Deployment
```

The explicit `Checkout` stage printed a teaching message; the real repository checkout was automatically performed by Declarative Pipeline's SCM stage.

## Final functional Jenkinsfile pattern

```groovy
pipeline {
    agent any

    environment {
        PATH         = "/usr/local/bin:/opt/homebrew/bin:${env.PATH}"
        IMAGE_NAME   = 'arun-jenkins-flask-app'
        IMAGE_TAG    = "build-${BUILD_NUMBER}"
        AWS_REGION   = 'us-east-1'
        AWS_ACCOUNT  = '160827082645'
        ECR_REPO     = 'arun-jenkins-flask-app'
        ECR_REGISTRY = "${AWS_ACCOUNT}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    }

    stages {
        stage('Checkout') {
            steps { echo 'Checking out source code...' }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker buildx build \
                      --platform linux/amd64 \
                      -f docker/Dockerfile \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      --load \
                      .
                '''
            }
        }

        stage('AWS CLI Check') {
            steps { sh 'aws --version' }
        }

        stage('AWS Identity Check') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh 'aws sts get-caller-identity'
                }
            }
        }

        stage('ECR Login') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh '''aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}'''
                }
            }
        }

        stage('Tag Docker Image') {
            steps { sh 'docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}' }
        }

        stage('kubectl CLI Check') {
            steps { sh 'kubectl version --client' }
        }

        stage('Push Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh 'docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}'
                }
            }
        }

        stage('Configure EKS Access') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        export KUBECONFIG="${WORKSPACE}/.kubeconfig"
                        aws eks update-kubeconfig --name arun-eks-cluster --region ${AWS_REGION} --kubeconfig "${KUBECONFIG}"
                        kubectl get nodes
                    '''
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        export KUBECONFIG="${WORKSPACE}/.kubeconfig"
                        kubectl set image deployment/arun-flask-deployment \
                          arun-flask-container=${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} -n arun-devops
                        kubectl rollout status deployment/arun-flask-deployment -n arun-devops --timeout=180s
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding', credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        export KUBECONFIG="${WORKSPACE}/.kubeconfig"
                        kubectl get deployment arun-flask-deployment -n arun-devops
                        kubectl get pods -n arun-devops -o wide
                        kubectl get service arun-flask-service -n arun-devops
                    '''
                }
            }
        }
    }
}
```

Several intermediate edits accidentally nested stages or closed `stages {}` too early. Inspecting the tail of the file before committing prevented syntax errors from reaching Jenkins:

```bash
cat Jenkinsfile
tail -n 40 Jenkinsfile
tail -n 50 Jenkinsfile
tail -n 60 Jenkinsfile
sed -n '18,35p' Jenkinsfile
git diff Jenkinsfile
```
