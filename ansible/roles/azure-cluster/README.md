Role Name
=========

Spin up a group of virtual machines in the same resource group and network

Requirements
------------

You must have the **python** `azure` module installed. (version >= 1.0.2). You can get this by running `pip install azure` or `sudo pip install azure`.

Because I couldn't get module embedding working in my role, you will need to find the corresponding library that is consumed by this role if you wish to use the role elsewhere.

Role Variables
--------------

Variables you *must* set:

* `state` - either `"absent"` or `"present"`
* `azure_subscription_id` - from subscriptions
* `azure_client_id` - from azure application page (Active Directory)
* `azure_client_secret` - from azure application page
* `azure_oauth_endpoint` - from azure application page
* `public_keys` - `.pem` file to upload to linux hosts

This roles exposes the following variables:

* `list_azure_ips` - actually a list of FQDNs of the virtual machines created. This is useful for adding hosts to inventories. The array will be stored in the `results` variable inside of `list_azure_ips`.

```yaml
- name: add hosts to inventory
  add_host: name={{ item.public_ip._dns_settings._fqdn }} group=zookeeper
  with_items: list_azure_ips.results
```

Dependencies
------------

No Dependencies.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - { role: username.rolename, x: 42 }

License
-------

BSD

Author Information
------------------

Jeffrey Gensler (jgensl2@uic.edu)
