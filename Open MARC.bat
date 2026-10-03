@echo off
rem Starts M.A.R.C on this laptop and opens it in your browser.
rem Keep this window open while you use M.A.R.C. Close it to stop.
cd /d "%~dp0"
start "" http://127.0.0.1:8765/MARC/
".venv\Scripts\python.exe" scripts\server.py
