import jenkinsapi
from jenkinsapi.jenkins import Jenkins

class job_checker:

    def __init__(self, J):
        self.J = J 

    def check_on_going_jobs(self, view_name):
        print "Start to check on going jobs for view " + view_name
        self.jobs_in_view = self.J.views[view_name].get_job_dict()
        self.on_going_jobs = []
        for job_name, joblink in self.jobs_in_view.iteritems():
            if self.J[job_name].is_running():
               #print "on-going job: " + job_name
               self.on_going_jobs.append(job_name)
        return self.on_going_jobs

    def check_jobs_in_view(self, view_name):
        print "Start to check jobs in view " + view_name
        self.jobs_in_view = self.J.views[view_name].get_job_dict()
        self.jobs_list = []
        for job_name, joblink in self.jobs_in_view.iteritems():
            self.jobs_list.append(job_name)
        return self.jobs_list

if __name__ == "__main__":

    j = job_checker("http://54.175.83.123/", "jenkins", "jenkins")
    on_going_jobs = j.check_on_going_jobs("k8s")
    print on_going_jobs

