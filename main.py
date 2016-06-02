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
    output, return_code = run_shell("kubectl get rc | grep jenkins-slave-1")
    global rc_to_be_deleted
    global label_name
    if return_code != 0:
        if not run_shell("kubectl create -f jenkins-slave-1.yaml")[1]:
            nice_print("Create rc jenkins-slave-1 successfully!")
            label_name="jenkins-slave-1"
            if not run_shell("kubectl get rc | grep jenkins-slave-2")[1]:
                rc_to_be_deleted="jenkins-slave-2"
            else: 
                nice_print("jenkins-slave-2 is not exist, no need to delete!")
        else:
            nice_print("Error creating rc jenkins-slave-1! Exiting...")
            sys.exit()
    else:
        if run_shell("kubectl get rc | grep jenkins-slave-2")[1]:
            if not run_shell("kubectl create -f jenkins-slave-2.yaml")[1]:
                nice_print("Create rc jenkins-slave-2 successfully!")
                label_name="jenkins-slave-2"
                rc_to_be_deleted="jenkins-slave-1"
            else:
                nice_print("Error creating rc jenkins-slave-2! Exiting...")
                sys.exit()
        else:
             nice_print("Both jenkins-slave-1 and jenkins-slave-2 are existing, Error!")
             sys.exit()

def check_on_going_job():
    '''Check on-going jobs under rc to be removed'''
    nice_print("Start to check on-going jobs")
    global job_pod_list
    job_pod_list = {}
    for i in eval(urllib.urlopen(jenkins_url + "/label/" + rc_to_be_deleted + "/api/python?pretty=true").read())['tiedJobs']:
        i = i['name']
        print "Starting to check job " + i
        if J[i].is_running():
            print "Job " + i + " is on-going"
            print "Change label of the pod to to-be-removed"
            pod_name_sufix = J[i].get_last_build().get_slave().split('-')[3]
            pod_name = rc_to_be_deleted + "-" + pod_name_sufix
            job_pod_list[i] = pod_name
            run_shell("kubectl label --overwrite pods " + pod_name + " name=to-be-removed")


def update_job_config():
    '''Update job config to backup replication controller'''
    nice_print("Start to update job config")
    for i in eval(urllib.urlopen(jenkins_url + "/label/" + rc_to_be_deleted + "/api/python?pretty=true").read())['tiedJobs']:
      i = i['name']
      print "Updating job config for " + i
      config=J[i].get_config()
      if label_name == "jenkins-slave-2":
        J[i].update_config(config.replace('jenkins-slave-1', 'jenkins-slave-2'))
      else:
        J[i].update_config(config.replace('jenkins-slave-2', 'jenkins-slave-1'))

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
    args = parser.parse_args()
    jenkins_url = args.url
    username = args.username
    token = args.token
    job_pod_list = []

    #Initialize connection
    J = jenkins_connector.jenkins_connector(jenkins_url, username, token).connect()
    
    main()

