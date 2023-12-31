def call(dockerRepoName, imageName, dirName) {
    pipeline {
        agent any
        parameters {
            booleanParam(defaultValue: false, description: 'Deploy the App', name: 'DEPLOY')
        }
        stages {
            stage('Build') {
                steps {
                    sh "pip install -r ${dirName}/requirements.txt --break-system-packages"
                }
            }

            stage('Security') {
                steps {
                    // sh "docker run -d ${dockerRepoName}:latest"
                    // sh "nmap --script vulners --script-args mincvss=7.5 -sV -Pn -p 8080 127.0.0.1 | grep '*EXPLOIT'"
                    sh "pip-audit --requirement ${dirName}/requirements.txt -l --ignore-vuln PYSEC-2023-221"

                }
            }

            stage('Lint'){
                steps{
                    sh "pylint --fail-under=5.0 ${dirName}/*.py"
                }
            }


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


            stage('Deploy'){
                when {
                    expression { params.DEPLOY }
                }
                steps{
                    sshagent(credentials: ['ssh-kafka']){
                        sh """ 
                            ssh -o StrictHostKeyChecking=no azureuser@20.63.112.52 '
                                cd Microservices_3855/Deployment &&
                                docker pull khushpreet688/${dockerRepoName}:${imageName} &&
                                docker-compose up -d'
                        """

                    }
                }
                
            }
        }
    }

}