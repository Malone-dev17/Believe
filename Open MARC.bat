@echo off
rem Opens M.A.R.C in your browser, starting it in the background if needed.
cd /d "%~dp0"
start "" ".venv\Scripts\pythonw.exe" scripts\launch.pyw
