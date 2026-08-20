pipeline {
    agent any

    environment {
	PATH       = "/usr/local/bin:${env.PATH}"
        IMAGE_NAME = 'arun-jenkins-flask-app'
        IMAGE_TAG  = "build-${BUILD_NUMBER}"
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
    }
}
