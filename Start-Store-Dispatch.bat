@echo off
cd /d "%~dp0"
where py >nul 2>nul
if errorlevel 1 (
 echo Python is needed. Install Python 3.11 or newer from python.org, then run this file again.
 pause
 exit /b 1
)
py -3 launcher.py
pause
