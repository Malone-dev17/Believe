@echo off
rem Stops the running M.A.R.C server, starts a fresh one (picks up new features) and opens it.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\restart.ps1"
