# CS 441: Cloud Computing

## Course Project: Scaling Zookeeper on Microsoft Azure

This first phase was to figure out how an application responds to load. The second phase was to use that data to integrate your application with the scaling features provided by Azure.

---

### What Is Included

There are two directories: `/ansible` and `/azure-service`. They are a result of the two phases of the course project.

#### ansible

There is a README in that directory describing what is needed to test out the Ansible work. Overall, there are scripts to spin up a Zookeeper cluster of a specified size, a node with ELK stack for data collection and visualization, and a node to run the JMeter tests from.

#### azure-service (incomplete)

There is a README in that directory describing what is needed to test out the Azure Service. Overall, this spins up a three node cluster AFTER the user has created a service. Almost all of this work is done though Eclipse's Azure plugin.

#### Report.pdf

I have detailed the results of my load tests and written about the goals of this project.
