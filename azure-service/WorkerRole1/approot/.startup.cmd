rd "\%ROLENAME%"

if defined DEPLOYROOT_PATH set DEPLOYROOT=%DEPLOYROOT_PATH%
if defined DEPLOYROOT (
	mklink /J "\%ROLENAME%" "%DEPLOYROOT%"
) else (
	mklink /J "\%ROLENAME%" "%ROLEROOT%\approot"
)

set DEPLOYROOT=\%ROLENAME%
set SERVER_APPS_LOCATION=%DEPLOYROOT%

set _JAVA_OPTIONS=-agentlib:jdwp=transport=dt_socket,server=y,address=8090,suspend=n


if not "%SERVER_APPS_LOCATION%" == "\%ROLENAME%" if exist "HelloWorld.war"\* (echo d | xcopy /y /e /q "HelloWorld.war" "%SERVER_APPS_LOCATION%\HelloWorld.war" 1>nul) else (echo f | xcopy /y /q "HelloWorld.war" "%SERVER_APPS_LOCATION%\HelloWorld.war" 1>nul)


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

@ECHO OFF
set ERRLEV=%ERRORLEVEL%
if %ERRLEV%==0 (echo Startup completed successfully.) else (echo *** Azure startup failed [%ERRLEV%]- exiting...)
timeout 5
exit %ERRLEV%