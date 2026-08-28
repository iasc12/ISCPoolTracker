@echo off
title ISC Pool Tracker

cd /d "%~dp0"

call venv\Scripts\activate.bat

echo.
echo ==========================================
echo        ISC POOL TRACKER
echo ==========================================
echo.
echo Starting application...
echo.

start "" http://127.0.0.1:8000

python manage.py runserver 127.0.0.1:8000

pause