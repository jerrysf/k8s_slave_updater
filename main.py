import job_updator
import jenkins_connector
import job_checker
import subprocess
import argparse
import sys
import urllib
from time import sleep


def run_shell(cmd):
    '''Utility to run command in Shell'''
    if dryrun == "yes":
      print "dryrun:  " + cmd
    else:
      p = subprocess.Popen(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE, shell=True)
      output, return_code = p.communicate()[0], p.returncode
      return output, return_code
    
def nice_print(content):
    '''Utility to have print better console output'''
    print "=" * 80
    print "= " + content + " ="
    print "=" * 80


def create_new_rc():
    '''Create new replication controller based on exsiting one'''
    nice_print("Start to create new rc by determing existing rc")
    output, return_code = run_shell("kubectl get rc | grep jenkins-slave-a")
    global rc_to_be_deleted
    global label_name
    if return_code != 0:
        if not run_shell("kubectl create -f jenkins-slave-a.yaml")[1]:
            nice_print("Create rc jenkins-slave-a successfully!")
            label_name="jenkins-slave-a"
            if not run_shell("kubectl get rc | grep jenkins-slave-b")[1]:
                rc_to_be_deleted="jenkins-slave-b"
            else: 
                nice_print("jenkins-slave-b is not exist, no need to delete!")
        else:
            nice_print("Error creating rc jenkins-slave-a! Exiting...")
            sys.exit()
    else:
        if run_shell("kubectl get rc | grep jenkins-slave-b")[1]:
            if not run_shell("kubectl create -f jenkins-slave-b.yaml")[1]:
                nice_print("Create rc jenkins-slave-b successfully!")
                label_name="jenkins-slave-b"
                rc_to_be_deleted="jenkins-slave-a"
            else:
                nice_print("Error creating rc jenkins-slave-b! Exiting...")
                sys.exit()
        else:
             nice_print("Both jenkins-slave-a and jenkins-slave-b are existing, Error!")
             sys.exit()

def check_on_going_job():
    '''Check on-going jobs under rc to be removed'''
    nice_print("Start to check on-going jobs")
    global job_pod_list
    job_pod_list = jc.check_on_going_jobs_with_node(jenkins_url, rc_to_be_deleted)
    for job, pod in job_pod_list:
        run_shell("kubectl label --overwrite pods " + pod + " name=to-be-removed")


def update_job_config():
    '''Update job config to backup replication controller'''
    nice_print("Start to update job config")
    url = '{0}/label/{1}/api/python?pretty=true'.format(jenkins_url, rc_to_be_deleted)
    job_list_with_url = eval(urllib.urlopen(url).read())['tiedJobs']
    job_list = []
    for i in job_list_with_url:
        i = i['name']
        job_list.append(i)
    if label_name == "jenkins-slave-b":
      jc.update_jobs(job_list,'jenkins-slave-a', 'jenkins-slave-b')
    else:
      jc.update_jobs(job_list,'jenkins-slave-b', 'jenkins-slave-a')


def delete_old_rc():
    '''Delete original replication controller once new one is in place'''
    global job_pod_list
    if not rc_to_be_deleted:
        nice_print("No rc need to be deleted, Exit now!")
        sys.exit()

    nice_print("Starting to delete old rc")
    print "RC to be deleted: " + rc_to_be_deleted
    run_shell("kubectl delete rc " + rc_to_be_deleted)

    nice_print("Starting to delete old pod gracefully")
    if len(job_pod_list) == 0:
        print "No job is on-going, Exit now!"
        sys.exit()
  
    while len(job_pod_list) != 0:
        for job in job_pod_list.keys():
            build_status = J[job].is_running()
            built_on = "jenkins-slave-" + J[job].get_last_build().get_slave().split('-')[2]
            if (build_status == False) or (built_on != rc_to_be_deleted):
                print "Job " + job + " Finished or running on new rc"
                print "Start to delete pod: " +  job_pod_list[job]
                run_shell("kubectl delete pod " + job_pod_list[job])
                del job_pod_list[job]
            else:
                print "Job " + job + " is still running, wait 10s..."
                sleep(10)
    nice_print("All on-going jobs running on old rc are finished!")

def main():
    '''Main function'''
    create_new_rc()
    check_on_going_job()
    update_job_config()
    delete_old_rc()

if __name__ == '__main__':
    #Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--url')
    parser.add_argument('--username')
    parser.add_argument('--token')
    parser.add_argument('--dryrun')
    args = parser.parse_args()
    jenkins_url = args.url
    username = args.username
    token = args.token
    dryrun = args.dryrun
    job_pod_list = []

    
    jc = jenkins_connector.create_jenkins_connector(jenkins_url, username, token)
    
    J = jenkins_connector.jenkins_connector(jenkins_url, username, token).api_wrapper()
    
    main()

