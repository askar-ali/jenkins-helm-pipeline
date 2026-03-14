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
    stage('Verify') {
      // Independent checks run in parallel to shorten the path to feedback.
      parallel {
        stage('Unit tests') {
          steps { sh 'python3 -I -m unittest discover -s app/tests' }
        }
        stage('Lint chart') {
          steps {
            sh 'helm lint chart -f chart/values-staging.yaml'
            sh 'helm lint chart -f chart/values-prod.yaml'
          }
        }
        stage('Shell scripts') {
          steps { sh 'shellcheck scripts/*.sh' }
        }
      }
    }

    stage('Build image') {
      steps {
        sh '''docker build -t $IMAGE:$TAG \
                --build-arg APP_VERSION=$TAG --build-arg VCS_REF=$GIT_COMMIT .'''
      }
    }

    stage('Scan and SBOM') {
      parallel {
        stage('Vulnerability gate') {
          // Fail on HIGH/CRITICAL findings that have a fix available.
          steps { sh 'trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1 --no-progress $IMAGE:$TAG' }
        }
        stage('SBOM') {
          steps {
            sh 'trivy image --format cyclonedx --output sbom-${TAG}.cdx.json $IMAGE:$TAG'
            archiveArtifacts artifacts: 'sbom-*.cdx.json', fingerprint: true
          }
        }
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
          input message: "Deploy ${TAG} to production?", ok: 'Deploy', submitter: 'release-managers'
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
    success { slackSend channel: '#deploys', color: 'good',    message: "OK ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.TAG}) ${env.BUILD_URL}" }
    failure { slackSend channel: '#deploys', color: 'danger',  message: "FAILED ${env.JOB_NAME} #${env.BUILD_NUMBER} (${env.TAG}) ${env.BUILD_URL}" }
    always  { sh 'docker image rm $IMAGE:$TAG || true' }
  }
}
