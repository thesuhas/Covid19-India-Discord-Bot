pipeline {
    agent any

    stages {
        stage ('installing requirements'){
            steps{
                sh 'pip3 install -r requirements.txt'
            }
        }

        stage('changing build id'){
            steps{
                sh '''
                export JENKINS_NODE_COOKIE=dontKillMe'''
                sh 'export BUILD_ID=dontKillMe'
            }
            
            
        }

        stage('Stopping earlier worker'){
            steps{
                sh '''
                pkill -f bot.py || true
 '''


            }
        }

        stage('starting updated worker'){
            steps{
                 sh 'JENKINS_NODE_COOKIE=dontKillMe'
                sh 'JENKINS_NODE_COOKIE=dontKillMe && python3 bot.py'

            }
            
        }
    }
}