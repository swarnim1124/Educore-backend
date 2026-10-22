pipeline {

    agent any

    environment {
        APP_DIR = "/var/www/html/dev"
        BRANCH = "main"
        SERVICE = "dev"
        PORT = "8010"
    }

    stages {

        stage('Update Code') {
            steps {
                sh """
                    cd ${APP_DIR}

                    echo "Fetching latest code..."
                    git fetch origin

                    echo "Switching to ${BRANCH} branch..."
                    git checkout ${BRANCH}

                    echo "Resetting to latest remote commit..."
                    git reset --hard origin/${BRANCH}
                """
            }
        }

        stage('Prepare Python Environment') {
            steps {
                sh """
                    cd ${APP_DIR}

                    if [ ! -d "venv" ]; then
                        echo "Creating Virtual Environment..."
                        python3 -m venv venv
                    else
                        echo "Virtual Environment already exists."
                    fi
                """
            }
        }

        stage('Install Dependencies') {
            steps {
                sh """
                    cd ${APP_DIR}

                    source venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                """
            }
        }

        stage('Validate Application') {
            steps {
                sh """
                    cd ${APP_DIR}

                    source venv/bin/activate

                    echo "Validating application..."

                    python -m py_compile index.py
                    python -c "import index"

                    echo "Validation Successful."
                """
            }
        }

    }

    post {

        success {
            echo "========================================"
            echo "Deployment Successful"
            echo "========================================"
        }

        failure {
            echo "========================================"
            echo "Deployment Failed"
            echo "========================================"
        }

        
    }
}