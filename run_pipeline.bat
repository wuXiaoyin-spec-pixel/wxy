@echo off
setlocal

set "KEYWORD=%~1"
set "LIMIT=%~2"

if "%KEYWORD%"=="" set "KEYWORD=dating"
if "%LIMIT%"=="" set "LIMIT=20"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    python -m venv .venv
)

call ".venv\Scripts\activate"

echo Installing Python requirements...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo Installing Playwright Chromium...
python -m playwright install chromium

echo Running local pipeline...
python main.py --keyword "%KEYWORD%" --limit "%LIMIT%"

endlocal
