"""Exploração (sem janela na tela): abre um livro (CÓPIA) na janela offscreen e grava um print.

    python explorar.py <livro.pdf> <saida.png>
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import faulthandler
_rastro = open(Path(__file__).resolve().parents[1] / "_cru" / "rastro.txt", "w")
faulthandler.dump_traceback_later(45, repeat=True, file=_rastro)

AQUI = Path(__file__).resolve().parents[1]
RAIZ = AQUI.parents[1]
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
os.environ["LOCALAPPDATA"] = str(AQUI / "_dados" / "explorar")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

from PySide6.QtWidgets import QApplication  # noqa: E402

print("qt", flush=True)
app = QApplication.instance() or QApplication([])
print("app", flush=True)
from ui.janela_principal import JanelaPrincipal  # noqa: E402


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


print("import ok", flush=True)
janela = JanelaPrincipal()
print("janela", flush=True)
janela.resize(1600, 1000)
janela.show()
janela.abrir_livro(sys.argv[1])
print("aberto", flush=True)
assentar(6)
janela.grab().save(sys.argv[2])
c = janela.tela_conferir
print("trilha:", type(c).__name__, [n for n in dir(c) if "trilha" in n or "ferrament" in n][:30])
if janela.previas is not None:
    janela.previas.parar()
janela.close()
