# Kubernetes based Jenkins Slaves Updator
Python utility to update k8s based Jenkins slaves without interrupting on-going jobs.

The idea is to have one replication controller working(jenkins-slave-1), while another one standby(jenkins-slave-2). On-going jobs will be relabeled before the old rc being deleted, therefore when performing rc replacement, on-going jobs will not be affected.

This script together with replication controllers's yaml files should be run under the k8s master machine.
