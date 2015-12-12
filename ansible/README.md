# Load Testing Zookeeper on Azure

## Playbooks

### spinup.yml

Brings up a Zookeeper cluster, ELK node, and JMeter node.

### spindown.yml

This is incomplete and destroying resources is best done by deleteing the resource group in the UI online.

### run-jmeter.yml

This runs a JMeter test run. Change the number of loops, number of iterations, and ramp time. **IT CAN TAKE UP TO 10 MINUTES TO SEE DATA IN KIBANA**

## Running

### Dependencies

* Ansible compatible azure install (pip module 1.0.2 should do)
* Azure project setup. [Here](https://azure-sdk-for-python.readthedocs.org/en/latest/resourcemanagementauthentication.html) is the guide.
  Specifically, you will need:
  * Subscription ID (from online portal)
  * OAuth endpoint (from online portal)
  * Client ID (from `azure account list`)
  * Client Secret (password used to log in to account using azure-cli)

Basically, you need to create a "project" in the OLD Azure UI, and generate a token for Ansible to use. I've included some pictures [in the `/Pictures` folder](/Pictures/README.md)

### Steps

#### 1. Create `groupvars/all.yml`

```yaml
# inside file

---
azure_subscription_id: "..."
azure_client_id: "..."
azure_client_secret: "..."
azure_oauth_endpoint: '...'

# note that this is a list and Key is in .pem format!!! There is a guide floating around on Microsoft's website on how to create one.
public_keys:
- "-----BEGIN CERTIFICATE-----"
```

#### 2. Spinning up the cluster

```bash
$ ansible-playbook -i hosts spinup.yml
```

#### 3. Running JMeter tests

```bash
$ ansible-playbook -i hosts_intermediate_file run-jmeter.yml
```

### Inspection/Debugging

```
$ ssh azureadmin@<< your app basename >>-1-ip.centralus.cloudapp.azure.com
```

You might have to do this to the ELK node and change the IP of kibana from `localhost` to that node's public IP. I don't quite remember :worried:

## Notes

Ansible's [azure module](http://docs.ansible.com/ansible/azure_module.html) is compatible with an older version of the azure package on pip. I have (hastily) written a new module to interface with [azure 1.0.2](https://pypi.python.org/pypi/azure/1.0.2)
