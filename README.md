# k8s_slave_updater
Python utility to update k8s based Jenkins slaves without interrupting on-going jobs.

The idea is to have one replication controller working(jenkins-slave-1), while another one standby(jenkins-slave-2). On-going jobs will be relabeled
before the old rc being deleted, therefore when performing rc replacement, the on-going jobs will not be affected.
