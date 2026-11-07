"""Sobe as duas demonstrações de reúso de uma vez (Ctrl+C encerra tudo).

Uso, a partir de qualquer diretório:

    python demonstracoes/run_all.py

Workshop:  http://127.0.0.1:8101
Hackathon: http://127.0.0.1:8102
"""
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
APPS = [
    ("demonstracoes.workshop.main", 8101),
    ("demonstracoes.hackathon.main", 8102),
]

processos = [
    subprocess.Popen(
        [sys.executable, "-m", "uvicorn", f"{modulo}:app", "--port", str(porta)],
        cwd=RAIZ,
    )
    for modulo, porta in APPS
]

print("Workshop:  http://127.0.0.1:8101")
print("Hackathon: http://127.0.0.1:8102")
print("Ctrl+C para encerrar.")

try:
    for processo in processos:
        processo.wait()
except KeyboardInterrupt:
    for processo in processos:
        processo.terminate()
