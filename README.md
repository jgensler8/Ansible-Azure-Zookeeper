# Zookeeper on Azure

## Why?

This project is for my Cloud Computing class at UIC. I am writing JMeter tests and Ansible deployment logic to learn more about infrastructure in the cloud.

See [their wiki page ](https://cwiki.apache.org/confluence/display/ZOOKEEPER/ServiceLatencyOverview) on some of the metrics that they have gathered.

## Objectives

- [ ] Write and Deploy Zookeeper with Ansible
- [ ] Write preliminary metric gathering in JMeter
- [ ] Write monitoring logic to scale Zookeeper based on performance metrics

## Running

The Ansible directory contains serveral useful scripts to test the application.

### Dependencies

* Ansible compatible azure install (pip module 1.0.2 should do)
* Azure project setup. [Here](https://azure-sdk-for-python.readthedocs.org/en/latest/resourcemanagementauthentication.html) is the guide.
  Specifically, you will need:
  * Subscription ID (from online portal)
  * OAuth endpoint (from online portal)
  * Client ID (from `azure account list`)
  * Client Secret (password used to log in to account using azure-cli)

### Playbooks

#### main.yml

The *whole* package. I don't recommend using this but :wink:.

#### spinup.yml

Brings up a ZK cluster in Azure.

#### spindown.yml

#### run-jmeter.yml

### Steps

#### 1. Login using azure-cli

```bash
$ azure login
#
# ... and follow the instructions given ...
#
```

#### 2. Edit `groupvars/all.yml`

```yaml
# inside file

---
azure_subscription_id: "..."
azure_client_id: "..."
azure_client_secret: "..."
```

#### 3. Encrypt `groupvars/all.yml`

```bash
$ ansible-vault encrypt groupvars/all.yml
``

## Notes

Ansible's [azure module](http://docs.ansible.com/ansible/azure_module.html) is compatible with an older version of the azure package on pip. I have (hastily) written a new module to interface with [azure 1.0.2](https://pypi.python.org/pypi/azure/1.0.2)
