pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\User\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        VENV   = '.venv-ci'
        REPO   = 'https://github.com/Glebwen/WebVueDjango.git'
    }

    options { timestamps() }

    stages {
        stage('Checkout') {
            steps {
                echo "Branch: ${env.BRANCH_NAME}  Commit: ${env.GIT_COMMIT}"
                checkout scm
            }
        }

        stage('Setup env') {
            steps {
                bat """
                    chcp 65001 > nul
                    if not exist %VENV% (
                        "${PYTHON}" -m venv %VENV%
                    )
                    "%VENV%\\Scripts\\python.exe" -m pip install --upgrade pip
                    "%VENV%\\Scripts\\python.exe" -m pip install -r requirements.txt
                """
            }
        }

        stage('Django check') {
            steps {
                bat """
                    chcp 65001 > nul
                    "%VENV%\\Scripts\\python.exe" manage.py check
                """
            }
        }

        stage('Tests') {
            steps {
                bat """
                    chcp 65001 > nul
                    if not exist reports mkdir reports
                    "%VENV%\\Scripts\\python.exe" -m pytest --junitxml=reports/junit.xml
                """
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Deploy') {
            when { branch 'main' }
            steps {
                echo '=== Deploy to C:\\deploy\\WebGleb5 ==='
                bat """
                    chcp 65001 > nul
                    if not exist C:\\deploy mkdir C:\\deploy
                    if exist C:\\deploy\\WebGleb5 (
                        cd /d C:\\deploy\\WebGleb5
                        git pull
                    ) else (
                        git clone %REPO% C:\\deploy\\WebGleb5
                    )
                    cd /d C:\\deploy\\WebGleb5
                    if not exist .venv (
                        "${PYTHON}" -m venv .venv
                    )
                    .venv\\Scripts\\python.exe -m pip install --upgrade pip
                    .venv\\Scripts\\python.exe -m pip install -r requirements.txt
                    .venv\\Scripts\\python.exe manage.py migrate --noinput
                    .venv\\Scripts\\python.exe manage.py collectstatic --noinput
                    .venv\\Scripts\\python.exe manage.py check
                """
                bat """
                    nssm restart WebGleb5Deploy || echo Service not installed yet, skipping restart
                """
            }
        }
    }

    post {
        success { echo 'Pipeline SUCCESS' }
        failure { echo 'Pipeline FAILED' }
    }
}