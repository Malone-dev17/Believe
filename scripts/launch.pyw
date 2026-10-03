"""Open M.A.R.C: start the local server in the background if it isn't running, then open the browser.

Run with pythonw (no console window). Safe to double-click repeatedly.
"""
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
URL = "http://127.0.0.1:8765/MARC/"


def running():
    with socket.socket() as s:
        s.settimeout(0.3)
        return s.connect_ex(("127.0.0.1", 8765)) == 0


if not running():
    pythonw = ROOT / ".venv" / "Scripts" / "pythonw.exe"
    flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    subprocess.Popen([str(pythonw if pythonw.exists() else sys.executable), str(ROOT / "scripts" / "server.py")],
                     cwd=ROOT, creationflags=flags, close_fds=True)
    for _ in range(50):
        if running():
            break
        time.sleep(0.1)

webbrowser.open(URL)
