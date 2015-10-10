# Zookeeper on Azure

## Why?

This project is for my Cloud Computing class at UIC. I am writing JMeter tests
and Ansible deployment logic to learn more about infrastructure in the cloud.

See [their wiki page ](https://cwiki.apache.org/confluence/display/ZOOKEEPER/ServiceLatencyOverview)
on some of the metrics that they have gathered.

## Objectives

- [ ] Write and Deploy Zookeeper with Ansible
- [ ] Write preliminary metric gathering in JMeter
- [ ] Write monitoring logic to scale Zookeeper based on performance metrics

## Running

The Ansible directory contains serveral useful scripts to test the application.

### Dependencies

Ansible compatible azure install (the pip module)

### main.yml

The *whole* package. I don't recommend using this but :wink:.

### spinup.yml

Brings up a ZK cluster in Azure.

### spindown.yml

### deploy
