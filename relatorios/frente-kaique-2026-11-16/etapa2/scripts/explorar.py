"""Exploração: abre o .exe empacotado (área escondida) com uma pasta de dados e descreve a tela.
Uso: python explorar.py <exe> <dados> <temp> <saida> [argumentos do exe...]"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import piloto_uia as P

exe, dados, temp, saida = map(Path, sys.argv[1:5])
P.abrir_log(saida / "explorar.txt")
proc = P.lancar_exe(exe, dados, temp, sys.argv[5:])
try:
    w = P.janela_principal(proc.pid)
    time.sleep(15)
    P.print_janela(w, saida / "explorar-1.png")
    P.descrever(w, saida / "explorar-1.txt")
    P.anotar("janelas", [x.window_text() for x in P.janelas_do_processo(proc.pid)])
finally:
    try:
        P.fechar(w)
        proc.wait(30)
    except Exception:
        proc.kill()
    P.anotar("saiu", proc.returncode)
