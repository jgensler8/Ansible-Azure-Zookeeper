:: *** This script will run whenever Azure starts this role instance.
:: *** This is where you can describe the deployment logic of your server, JRE and applications 
:: *** or specify advanced custom deployment steps
::     (Note though, that if you're using this in Eclipse, you may find it easier to configure the JDK,
::     the server and the server and the applications using the New Azure Deployment Project wizard 
::     or the Server Configuration property page for a selected role.)

@echo off

:: Make sure we can run Powershell
powershell -command "Set-ExecutionPolicy Unrestricted" 2>> err.out

:: Install jdk
START /WAIT jre/jdk-7u79-windows-x64.exe /s

:: Bootstrap the rest
cd util
powershell .\bootstrap.ps1 2>> err.out