@echo off
cd /d "%~dp0"
if exist "Thrift Mart Dispatch Server Console.exe" (
 start "" "%SystemRoot%\System32\conhost.exe" "%~dp0Thrift Mart Dispatch Server Console.exe" --console
 exit /b 0
)
if exist "Thrift Mart Dispatch Server.exe" (
 start "" "Thrift Mart Dispatch Server.exe"
 exit /b 0
)
title Thrift Mart Dispatch Server
if exist "runtime\python.exe" (
 "runtime\python.exe" launcher.py
) else (
 py -3 launcher.py
)
pause
