jmeter-testrun
=========

Template a load test and run against a set of hosts

Requirements
------------

Requires JMeter to be installed and locatable at a varible named `jmeter_root`

Role Variables
--------------

Required:
* `jmeter_root`
* `test_plan` a complex object containing a JMeter JMX

Dependencies
------------

* jmeter (jgensler8)

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

An optional section for the role authors to include contact information, or a website (HTML is not allowed).
