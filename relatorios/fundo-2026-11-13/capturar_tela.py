"""Captura, SEM JANELA NA TELA (offscreen), o painel "Filtro da página" e o menu Filtro com o
"Desfazer o tirar o fundo" (D-699), na versão nova.

    python capturar_tela.py <raiz do código> <pasta de saída> <cópia do Siebmacher>
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

RAIZ, SAIDA, LIVRO = Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3]
SAIDA.mkdir(parents=True, exist_ok=True)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
dados = Path(tempfile.mkdtemp(prefix="fundo-tela-"))
os.environ["LOCALAPPDATA"] = str(dados / "dados")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

from PySide6.QtWidgets import QAbstractButton, QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir()
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])
from ui.janela_principal import JanelaPrincipal  # noqa: E402


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


janela = JanelaPrincipal()
janela.resize(1600, 1000)
janela.show()
janela.abrir_livro(LIVRO)
assentar(0.5)
next(b for b in janela.aviso_do_fundo.findChildren(QAbstractButton)
     if b.text() == "Sim, tirar o fundo").click()
conferir = janela.tela_conferir
conferir.ir_para_pagina(2)
painel = conferir.paineis.filtro_da_pagina
from ui.widgets.paineis import PAINEL_FILTRO  # noqa: E402

conferir.paineis.abrir(PAINEL_FILTRO)
assentar(8)
janela.grab().save(str(SAIDA / "janela.png"))
painel.grab().save(str(SAIDA / "painel-filtro.png"))
janela._marcar_o_filtro_no_menu()
menu = janela.menu.menus["Filtro"]
menu.popup(janela.mapToGlobal(janela.rect().topLeft()))
assentar(0.5)
menu.grab().save(str(SAIDA / "menu-filtro.png"))
menu.hide()
if janela.previas is not None:
    janela.previas.parar()
janela.close()
print("pronto")
