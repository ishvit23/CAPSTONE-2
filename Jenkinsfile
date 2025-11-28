pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BACKEND = "docker.io/ishvit23/digibuddy-backend"
        DOCKER_IMAGE_FRONTEND = "docker.io/ishvit23/digibuddy-frontend"
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

        stage('UI Tests') {
            steps {
                sh '''
                set -euo pipefail

                kubectl port-forward -n digibuddy svc/frontend-service 30080:80 >/tmp/pf.log 2>&1 &
                PF_PID=$!
                trap "kill $PF_PID || true" EXIT

                rm -rf selenium-venv
                python3 -m venv selenium-venv
                . selenium-venv/bin/activate
                pip install --upgrade pip
                pip install -r tests/selen/requirements.txt
                pytest tests/selen -v --junitxml=tests/selen/report.xml
                deactivate
                '''
            }
            post {
                always {
                    junit allowEmptyResults: true, testResults: 'tests/selen/report.xml'
                }
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
                set -e
                kubectl apply -f ${K8S_MANIFEST_DIR}/namespace.yaml || true
                if [ -f ${K8S_MANIFEST_DIR}/secret.yaml ]; then
                  kubectl apply -f ${K8S_MANIFEST_DIR}/secret.yaml
                else
                  echo "Skipping ${K8S_MANIFEST_DIR}/secret.yaml (file not committed)"
                fi
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

