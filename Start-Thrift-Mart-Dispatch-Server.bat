@echo off
title Thrift Mart Dispatch Server
cd /d "%~dp0"
if exist "runtime\python.exe" (
 "runtime\python.exe" launcher.py
) else (
 py -3 launcher.py
)
pause
