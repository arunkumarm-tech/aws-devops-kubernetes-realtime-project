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
    }
}
