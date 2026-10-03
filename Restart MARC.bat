@echo off
rem Stops the running M.A.R.C server and starts it again (picks up new features), then opens it.
cd /d "%~dp0"
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name like 'python%%'\" | Where-Object { $_.CommandLine -match 'scripts\\server.py' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }"
timeout /t 1 >nul
start "" ".venv\Scripts\pythonw.exe" scripts\launch.pyw
