@echo off
echo.
echo ========================================
echo    MailMate - AI Email Management
echo ========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

:: Check if .env file exists
if not exist ".env" (
    echo.
    echo No .env file found. Running setup...
    python setup_demo.py
    goto :end
)

:: Main menu
:menu
cls
echo.
echo ========================================
echo    MailMate - AI Email Management
echo ========================================
echo.
echo Choose an option:
echo.
echo 1. Launch Dashboard (Main Application)
echo 2. Run Setup Demo
echo 3. Process Emails (CLI)
echo 4. Daily Digest
echo 5. Health Check
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto dashboard
if "%choice%"=="2" goto demo
if "%choice%"=="3" goto process
if "%choice%"=="4" goto digest
if "%choice%"=="5" goto health
if "%choice%"=="6" goto end
goto menu

:dashboard
echo.
echo Launching MailMate Dashboard...
echo Visit: http://localhost:8501
echo Press Ctrl+C to stop the server
echo.
python main.py dashboard
goto menu

:demo
echo.
echo Running Setup Demo...
python setup_demo.py
pause
goto menu

:process
echo.
echo Processing emails...
python main.py process
pause
goto menu

:digest
echo.
echo Generating daily digest...
python main.py digest --speak
pause
goto menu

:health
echo.
echo Running health check...
python main.py health
pause
goto menu

:end
echo.
echo Thank you for using MailMate!
echo.
pause
