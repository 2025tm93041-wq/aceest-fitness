pipeline {
    agent any
    triggers { pollSCM('H/2 * * * *') }

    environment {
        IMAGE = "aceest-fitness:${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Clean Build Environment') {
            steps {
                sh 'rm -rf .venv && python3 -m venv .venv'
                sh '.venv/bin/pip install -r requirements-dev.txt'
            }
        }
        stage('Lint') {
            steps { sh '.venv/bin/flake8 .' }
        }
        stage('Unit Tests') {
            steps { sh '.venv/bin/pytest -v' }
        }
        stage('Docker Build') {
            steps { sh 'docker build -t $IMAGE .' }
        }
    }

    post {
        success { echo 'BUILD SUCCESS' }
        failure { echo 'BUILD FAILED - check the console output' }
        always  { sh 'docker image prune -f || true' }
    }
}
