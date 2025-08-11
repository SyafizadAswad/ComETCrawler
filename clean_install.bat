@echo off
echo COM-ET Crawler - Clean Installation
echo ===================================
echo.

echo Removing existing virtual environment...
if exist venv (
    rmdir /s /q venv
    echo Removed old virtual environment.
) else (
    echo No existing virtual environment found.
)

echo.
echo Creating fresh virtual environment...
python -m venv venv

echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies (pure Python packages only)...
pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo To run the application:
echo   run_crawler_venv.bat
echo.
echo To verify installation:
echo   python verify_install.py
echo.
pause 