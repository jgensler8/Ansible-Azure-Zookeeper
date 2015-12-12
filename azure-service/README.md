# Azure Zookeeper Cloud Service (incomplete)

## Setup

### 1. Download Eclipse

I used Mars.

### 2. Download Azure Plugin

[Here is the link](https://azure.microsoft.com/en-us/documentation/articles/azure-toolkit-for-eclipse-installation/)

### 3. Create A New Azure Deployment project

Apparently, `Import` doesn't work so we have to copy the project manually.

### 4. Copy Files Over


Overwrite the following:

* `ServiceConfiguration.cscfg`
* `ServiceDefinition.csdef`
* `WorkerRole1/approot/run.cmd`
* `WorkerRole1/approot/startup.cmd`

Add the following:

* `WorkerRole1/approot/util/bootstrap.ps1`
* `WorkerRole1/approot/util/run.ps1`

### 4. Download Ant, JDK, Zookeeper

Create the following directories:

* `WorkerRole1/approot/jre`
* `WorkerRole1/approot/ant`
* `WorkerRole1/approot/zookeeper`

Download the following versions of software into their respective directory:

* jdk-7u79-windows-x64.exe (yes, the directory is named jre even though this is the jdk)
* apache-ant-1.9.6
* zookeeper-3.4.7

### 5. Check That It Looks OK

## Running

Simply click the button to deploy to Azure. You will need to get your `*.PublishSettings` file for your subscription. Supply Login information if you wish to RDP to the servers.
