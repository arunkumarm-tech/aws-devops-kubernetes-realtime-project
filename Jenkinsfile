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
            steps {
                echo 'Checking out source code...'
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build \
                      -f docker/Dockerfile \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      .
                '''
            }
        }
stage('AWS CLI Check') {
    steps {
        sh 'aws --version'
    }
}

        stage('AWS Identity Check') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-devops-credentials']]) {
                    sh 'aws sts get-caller-identity'
                }
            }
        }

        stage('ECR Login') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        aws ecr get-login-password --region ${AWS_REGION} \
                        | docker login \
                          --username AWS \
                          --password-stdin ${ECR_REGISTRY}
                    '''
                }
            }
        }

        stage('Tag Docker Image') {
            steps {
                sh '''
                    docker tag \
                      ${IMAGE_NAME}:${IMAGE_TAG} \
                      ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                '''
            }
        }

        stage('kubectl CLI Check') {
            steps {
                sh 'kubectl version --client'
            }
        }

        stage('Push Image to ECR') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        docker push ${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG}
                    '''
                }
            }
        }

        stage('Configure EKS Access') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        export KUBECONFIG="${WORKSPACE}/.kubeconfig"

                        aws eks update-kubeconfig \
                          --name arun-eks-cluster \
                          --region ${AWS_REGION} \
                          --kubeconfig "${KUBECONFIG}"

                        kubectl get nodes
                    '''
                }
            }
        }

        stage('Deploy to EKS') {
            steps {
                withCredentials([[$class: 'AmazonWebServicesCredentialsBinding',
                                  credentialsId: 'aws-devops-credentials']]) {
                    sh '''
                        export KUBECONFIG="${WORKSPACE}/.kubeconfig"

                        kubectl set image deployment/arun-flask-deployment \
                          arun-flask-container=${ECR_REGISTRY}/${ECR_REPO}:${IMAGE_TAG} \
                          -n arun-devops

                        kubectl rollout status deployment/arun-flask-deployment \
                          -n arun-devops \
                          --timeout=180s
                    '''
                }
            }
        }
    }
}
