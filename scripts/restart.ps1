# Stops every running M.A.R.C server, then starts a fresh one and opens it in the browser.
$root = Split-Path $PSScriptRoot -Parent
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -like 'python*' -and $_.CommandLine -match 'command-centre\\scripts\\server\.py' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 1
Start-Process -FilePath (Join-Path $root '.venv\Scripts\pythonw.exe') `
  -ArgumentList ('"' + (Join-Path $root 'scripts\launch.pyw') + '"') -WorkingDirectory $root
