@echo off
echo COM-ET Product Diagram Downloader
echo =================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting application...
python com_et_crawler.py

echo.
echo Application closed.
pause 