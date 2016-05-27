import jenkinsapi
from jenkinsapi.jenkins import Jenkins

class jenkins_connector:

    def __init__(self, jenkins_url, username, password):
        self.jenkins_url = jenkins_url
        self.username = username
        self.password = password
        self.J = Jenkins(self.jenkins_url, self.username, self.password)

    def connect(self):
        return self.J

