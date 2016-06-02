import jenkinsapi
from jenkinsapi.jenkins import Jenkins

class jenkins_connector:
    '''jenkinsapi wrapper, connect to jenkins via token'''

    def __init__(self, jenkins_url, username, password):
        self.jenkins_url = jenkins_url
        self.username = username
        self.password = password
        self.J = Jenkins(self.jenkins_url, self.username, self.password)
        
    def api_wrapper(self):        
        return self.J
    
    def check_on_going_jobs_with_node(self, jenkins_url, label_name):
        print "Start to check on going jobs under label " + label_name
        job_pod_list = {}
        url = '{0}/label/{1}/api/python?pretty=true'.format(jenkins_url, label_name)
        for i in eval(urllib.urlopen(url).read())['tiedJobs']:
            i = i['name']
            print "Starting to check job " + i
            if J[i].is_running():
                print "Job " + i + " is on-going"
                print "Change label of the pod to to-be-removed"
                pod_name_sufix = J[i].get_last_build().get_slave().split('-')[3]
                pod_name = label_name + "-" + pod_name_sufix
                job_pod_list[i] = pod_name
        return job_pod_list        

    def check_jobs_in_view(self, view_name):
        print "Start to check jobs in view " + view_name
        self.jobs_in_view = self.J.views[view_name].get_job_dict()
        self.jobs_list = []
        for job_name, joblink in self.jobs_in_view.iteritems():
            self.jobs_list.append(job_name)
        return self.jobs_list
    
    def update_jobs(self, job_list, original_text, new_text):
        self.job_list = job_list
        for job in job_list:
            self.config=self.J[job].get_config()
            self.J[job].update_config(self.config.replace(original_text, new_text))

def create_jenkins_connector(jenkins_url, username, password):
    jc = jenkins_connector(jenkins_url, username, password)
    return jc

