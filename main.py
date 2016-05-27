import job_updator
import jenkins_connector
import job_checker

jenkins_url="http://54.175.83.123/"
username="jenkins"
password="jenkins"
J = jenkins_connector.jenkins_connector(jenkins_url, username, password).connect()

checker = job_checker.job_checker(J) 
on_going_jobs = checker.check_on_going_jobs("k8s")
print on_going_jobs

#updator = job_updator.job_updator("http://54.175.83.123/", "jenkins", "jenkins")
#updator.update_jobs(on_going_jobs, "jenkins-slave-1", "jenkins-slave-2")
