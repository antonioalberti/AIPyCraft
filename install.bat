@echo off
title AIPyCraft Installation

echo Checking for requirements.txt...
if not exist requirements.txt (
    echo ERROR: requirements.txt not found in the current directory.
    pause
    exit /b 1
)

echo Creating Python virtual environment (venv)...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment. Make sure Python 3 is installed and in your PATH.
    pause
    exit /b 1
)

echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat && python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies from requirements.txt. Check the output above for details.
    pause
    exit /b 1
)

echo.
echo Installation complete.
echo You can now run the application using 'python main.py'.
echo If you want to manually activate the environment later, run: venv\Scripts\activate.bat
echo.
pause
exit /b 0
