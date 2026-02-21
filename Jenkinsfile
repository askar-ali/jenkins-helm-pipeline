pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    timeout(time: 30, unit: 'MINUTES')
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }

  environment {
    REGISTRY = 'registry.example.internal'
    IMAGE    = "${REGISTRY}/sample"
    TAG      = "${env.GIT_COMMIT?.take(8) ?: env.BUILD_NUMBER}"
  }

  stages {
    stage('Test') {
      steps { sh 'python3 -m unittest discover -s app/tests' }
    }

    stage('Lint chart') {
      steps { sh 'helm lint chart' }
    }

    stage('Build image') {
      steps { sh 'docker build -t $IMAGE:$TAG .' }
    }

    stage('Scan image') {
      steps {
        // Gate: fail on HIGH/CRITICAL findings.
        sh 'trivy image --severity HIGH,CRITICAL --exit-code 1 --no-progress $IMAGE:$TAG'
      }
    }

    stage('Push image') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(credentialsId: 'registry-creds',
                         usernameVariable: 'REG_USER', passwordVariable: 'REG_PASS')]) {
          sh 'echo "$REG_PASS" | docker login $REGISTRY -u "$REG_USER" --password-stdin'
          sh 'docker push $IMAGE:$TAG'
        }
      }
    }

    stage('Deploy staging') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-staging', variable: 'KUBECONFIG')]) {
          sh 'scripts/deploy.sh staging $TAG'
          sh 'scripts/smoke-test.sh staging'
        }
      }
    }

    stage('Approve production') {
      when { branch 'main' }
      steps {
        timeout(time: 1, unit: 'HOURS') {
          input message: "Deploy ${TAG} to production?", ok: 'Deploy'
        }
      }
    }

    stage('Deploy production') {
      when { branch 'main' }
      steps {
        withCredentials([file(credentialsId: 'kubeconfig-prod', variable: 'KUBECONFIG')]) {
          sh 'scripts/deploy.sh prod $TAG'
          sh 'scripts/smoke-test.sh prod'
        }
      }
    }
  }

  post {
    always  { sh 'docker image rm $IMAGE:$TAG || true' }
    failure { echo 'Pipeline failed - see the failing stage above.' }
  }
}
