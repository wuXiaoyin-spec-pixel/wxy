@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

if not exist ".venv" (
    echo [INFO] Creating virtual environment...
    py -m venv .venv
)

call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo [ERROR] Failed to activate virtual environment.
    exit /b 1
)

echo [INFO] Installing/updating dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    exit /b 1
)

echo [INFO] Installing Playwright Chromium (if needed)...
python -m playwright install chromium
if errorlevel 1 (
    echo [WARN] Playwright browser install returned non-zero. Continuing...
)

set "KEYWORD=%~1"
if "%KEYWORD%"=="" (
    set /p KEYWORD=Enter keyword for Ad Library search (default: dating): 
)
if "%KEYWORD%"=="" set "KEYWORD=dating"

set "LIMIT=%~2"
if "%LIMIT%"=="" set "LIMIT=50"

echo [INFO] Running pipeline with keyword: %KEYWORD% and limit: %LIMIT%
python main.py --keyword "%KEYWORD%" --limit %LIMIT%
set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE%==0 (
    echo [SUCCESS] Pipeline completed.
) else (
    echo [ERROR] Pipeline failed with exit code %EXIT_CODE%.
)

deactivate
exit /b %EXIT_CODE%
