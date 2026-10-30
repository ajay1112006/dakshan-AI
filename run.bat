@echo off
REM Quick launcher for Dakshan AI
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set REBUILD_VENV=0
if not exist ".venv\Scripts\python.exe" (
    set REBUILD_VENV=1
) else (
    .\.venv\Scripts\python.exe -c "import sys" >nul 2>&1
    if errorlevel 1 (
        echo [INFO] Detected an invalid or copied virtual environment.
        echo Resetting and rebuilding virtual environment for this computer...
        rmdir /s /q .venv
        set REBUILD_VENV=1
    )
)

if "%REBUILD_VENV%"=="1" (
    echo Setting up virtual environment...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERROR] Python is not installed or not added to PATH.
        echo Please install Python 3 and ensure 'Add python.exe to PATH' is checked.
        pause
        exit /b 1
    )
    echo Installing required packages...
    .\.venv\Scripts\pip install -r requirements.txt
)

.\.venv\Scripts\python chatbot.py
pause

