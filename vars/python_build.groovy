def call(dockerRepoName, imageName, portNum, dirName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage('Build') {
                steps {
                    sh "pip install -r ${dirName}/requirements.txt --break-system-packages"
                    sh "pip install --upgrade flask --break-system-packages" 
                }
            }

            stage('Lint'){
                steps{
                    sh "pylint --fail-under=5.0 ${dirName}/*.py"
                }
            }

            // stage('Security'){
            //     steps{
            //         sh 'nmap '
            //     }
            // }

            stage('Package') {
                when {
                    expression { env.GIT_BRANCH == 'main' }
                }
                steps {
                    withCredentials([string(credentialsId: 'DockerHub', variable: 'TOKEN')]) {
                        sh "docker login -u 'khushpreet688' -p '$TOKEN' docker.io"
                        sh "docker build -t ${dockerRepoName}:latest --tag khushpreet688/${dockerRepoName}:${imageName} ./${dirName}"
                        sh "docker push khushpreet688/${dockerRepoName}:${imageName}"
                    }
                }
            }


            // stage('Package2') {
            //     steps{
            //         sh 'zip app.zip *.py'
            //         archiveArtifacts artifacts: 'app.zip'
            //     }
            // }

            stage('Deliver'){
                when {
                    expression { params.DEPLOY }
                }
                steps {
                    sh "docker stop ${dockerRepoName} || true"
                    sh "docker rm ${dockerRepoName} || true"
                    // sh "docker run -d –p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
                    sh "docker run -d -p ${portNum}:${portNum} --name ${dockerRepoName} ${dockerRepoName}:latest"
                }
            }
        }
    }

}