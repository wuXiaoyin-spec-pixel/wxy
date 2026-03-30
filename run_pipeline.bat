@echo off
setlocal

set "KEYWORDS=%~1"
set "LIMIT=%~2"
set "KEYWORD_FILE=%~3"

if "%KEYWORDS%"=="" set "KEYWORDS=dating"
if "%LIMIT%"=="" set "LIMIT=30"

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
if not "%KEYWORD_FILE%"=="" (
    python main.py --keywords "%KEYWORDS%" --keyword-file "%KEYWORD_FILE%" --limit "%LIMIT%"
) else (
    python main.py --keywords "%KEYWORDS%" --limit "%LIMIT%"
)

endlocal
