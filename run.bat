@echo off
setlocal
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo First run: setting up Piper...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
    if errorlevel 1 (
        echo.
        echo Setup failed.
        pause
        exit /b 1
    )
)

".venv\Scripts\python.exe" "%~dp0tts.py"
if errorlevel 1 pause
