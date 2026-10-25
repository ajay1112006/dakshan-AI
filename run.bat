@echo off
REM Quick launcher for Dakshan AI
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Setting up environment...
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements.txt
)

.\.venv\Scripts\python chatbot.py
pause
