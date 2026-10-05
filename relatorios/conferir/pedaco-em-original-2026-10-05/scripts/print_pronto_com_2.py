r"""Print da tela "Ficou pronto!" quando o PDF antigo estava aberto em outro
programa e o novo foi salvo como "(2)" (conserto de 05/10/2026), e da mesma
tela no caso normal, para comparar. Sem janela na tela (offscreen): a TelaFinal
sozinha, com a folha de estilo do programa, no tamanho 1280 x 657 (o do
notebook do Kaique a 150%). PDFs de mentira numa pasta temporaria, apagada no fim.

Uso: .venv\Scripts\python.exe relatorios\conferir\pedaco-em-original-2026-10-05\scripts\print_pronto_com_2.py
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")     # o offscreen nao acha as fontes sozinho
AQUI = Path(__file__).resolve().parents[1]
RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import fitz  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from modelos import Projeto  # noqa: E402
from ui.estilo import FOLHA_DE_ESTILO  # noqa: E402
from ui.tela_final import TelaFinal  # noqa: E402

app = QApplication.instance() or QApplication([])
app.setStyleSheet(FOLHA_DE_ESTILO)
pasta = Path(tempfile.mkdtemp(prefix="print_pronto_"))
try:
    novo = pasta / "Escola de Jesus - original (2).pdf"
    doc = fitz.open()
    for _ in range(10):
        doc.new_page()
    doc.save(str(novo))
    doc.close()
    projeto = Projeto(caminho_entrada="x.pdf")
    for nome, antigo in (("pronto-com-2.png", "Escola de Jesus - original.pdf"),
                         ("pronto-normal.png", "")):
        tela = TelaFinal()
        tela.resize(1280, 657)
        tela.mostrar(projeto, str(novo), 10, 10, antigo_preso=antigo)
        tela.show()
        app.processEvents()
        tela.grab().save(str(AQUI / nome))
        print("gravado", nome)
        tela.close()
finally:
    shutil.rmtree(pasta, ignore_errors=True)
