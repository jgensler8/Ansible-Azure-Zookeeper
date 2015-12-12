# install jdk
#../jre/jdk-7u79-windows-x64.exe /passive

# Move Java to avoid space filled path
mkdir D:\Java
Copy-Item "D:\Program Files\Java\jdk1.7.0_79\*" "D:\Java" -Recurse

# Set Java vars so scripts can run it
$env:JAVA_HOME = "D:\Java"
$env:JAVA = $env:JAVA_HOME + "\bin\java.exe"
$env:Path += ";" + $env:JAVA_HOME + "\bin"

# build zookeeper
../ant/apache-ant-1.9.6/bin/ant.bat -f ../zookeeper/zookeeper-3.4.7

# template id file ?

# template config file ?