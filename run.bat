@echo off
echo Starting MarkItDown Converter...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment and run the app
call venv\Scripts\activate.bat && python app.py

pause