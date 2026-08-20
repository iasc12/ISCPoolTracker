@echo off
cd /d C:\Users\isaac\ISCPoolTracker

call venv\Scripts\activate.bat

python manage.py send_daily_reminder