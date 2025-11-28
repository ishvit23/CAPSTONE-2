pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BACKEND = "your-registry/digibuddy-backend"
        DOCKER_IMAGE_FRONTEND = "your-registry/digibuddy-frontend"
        K8S_MANIFEST_DIR = "k8s"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Backend Image') {
            steps {
                dir('Backend_new') {
                    sh 'docker build -t $DOCKER_IMAGE_BACKEND:${BUILD_NUMBER} .'
                }
            }
        }

        stage('Build Frontend Image') {
            steps {
                sh 'docker build --build-arg VITE_API_BASE_URL=/api -t $DOCKER_IMAGE_FRONTEND:${BUILD_NUMBER} .'
            }
        }

        stage('Push Images') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                    echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                    docker push $DOCKER_IMAGE_BACKEND:${BUILD_NUMBER}
                    docker push $DOCKER_IMAGE_FRONTEND:${BUILD_NUMBER}
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh """
                kubectl apply -f ${K8S_MANIFEST_DIR}/namespace.yaml || true
                kubectl apply -f ${K8S_MANIFEST_DIR}/secret.yaml
                kubectl apply -f ${K8S_MANIFEST_DIR}/configmap.yaml
                kubectl apply -f ${K8S_MANIFEST_DIR}/mongodb-deployment.yaml
                kubectl apply -f ${K8S_MANIFEST_DIR}/backend-deployment.yaml
                kubectl apply -f ${K8S_MANIFEST_DIR}/frontend-deployment.yaml
                """
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed. Please check the logs.'
        }
        success {
            echo 'Pipeline completed successfully.'
        }
    }
}

