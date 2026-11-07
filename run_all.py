"""Sobe os 4 processos (3 microsserviços + gateway) de uma vez. Ctrl+C encerra tudo.

Uso: python run_all.py   ->   abra http://127.0.0.1:8000
"""
import subprocess
import sys

APPS = [("services.events.main:app", 8001), ("services.participants.main:app", 8002),
        ("services.registrations.main:app", 8003), ("gateway.main:app", 8000)]

procs = [subprocess.Popen([sys.executable, "-m", "uvicorn", app, "--port", str(port)])
         for app, port in APPS]
print("Confera em http://127.0.0.1:8000  (Ctrl+C para encerrar)")
try:
    for p in procs:
        p.wait()
except KeyboardInterrupt:
    for p in procs:
        p.terminate()
