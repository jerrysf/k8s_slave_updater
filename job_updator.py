import jenkinsapi
from jenkinsapi.jenkins import Jenkins

class job_updator:

    def __init__(self, J):
        self.J = J

    def update_jobs(self, job_list, original_text, new_text):
        self.job_list = job_list
        for job in job_list:
            self.J[job].update_config(config.replace(original_text, new_text))

