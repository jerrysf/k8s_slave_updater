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

job_in_view = checker.check_jobs_in_view("k8s")
print job_in_view

updator = job_updator.job_updator(J)
updator.update_jobs(job_in_view, "jenkins-slave-1", "jenkins-slave-2")
