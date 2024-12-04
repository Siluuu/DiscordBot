@echo off

cls

echo Updating repository from GitHub...
git pull origin main

if errorlevel 1 (
    echo Failed to pull the latest changes from GitHub.
    exit /b 1
)

set VENV_DIR=venv

if not exist %VENV_DIR% (
    echo Creating virtual environment...
    python -m venv %VENV_DIR%

    echo Activating virtual environment and installing requirements...
    call %VENV_DIR%\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo Virtual environment already exists.
)

call %VENV_DIR%\Scripts\activate.bat

if errorlevel 1 (
    echo Failed to activate Virtual environment.
    exit /b 1
)

cls

start /B python "run_discord.py"
start /B python "run_twitch.py"

pause
