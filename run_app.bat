@echo off
echo ===================================================
echo Starting Document Forgery AI (Unified Server)
echo ===================================================

cd /d "%~dp0"

REM Activate virtualenv and start uvicorn
if exist .venv\Scripts\python.exe (
    set "PYTHON_EXE=.venv\Scripts\python.exe"
) else (
    set "PYTHON_EXE=python"
)

echo Starting Backend & Web Dashboard on http://localhost:8000 ...
cd backend
"%~dp0%PYTHON_EXE%" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
pause
