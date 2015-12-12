#Set up Java vars
$env:JAVA_HOME = "D:\Java"
$env:JAVA = $env:JAVA_HOME + "\bin\java.exe"
$env:Path += ";" + $env:JAVA_HOME + "\bin"

# run zookeeper
zookeeper/zookeeper-3.4.7/bin/zkServer.cmd

# run REST server
ant/apache-ant-1.9.6/bin/ant.bat -f zookeeper/zookeeper-3.4.7/src/contrib/rest/build.xml run

echo "RUNNING!"

# netstat -a
# while($true)
#{
#	netstat -a
#	Start-Sleep -s 10
#}