"""Pergunta C (Girar como ferramenta), SEM JANELA NA TELA (offscreen, com as fontes do Windows).

    python girar_c.py <cópia do Gradus> <pasta de saída>

Como é HOJE, na versão de teste: abre o Gradus (cópia), vai à página 6 (uma página de texto
dividida), abre o painel Propriedades e escolhe, uma de cada vez, as ferramentas Cortar as bordas,
Endireitar e Retângulo (marcar). Em cada uma grava a janela inteira: o bloco "Girar a página" fica
no alto do Propriedades nas três. Grava também os três botões do canto da página e a lista do
"aplicar em" aberta. Nada do programa muda; dados numa pasta à parte.
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parents[1]
RAIZ = AQUI.parents[1]
LIVRO, SAIDA = sys.argv[1], Path(sys.argv[2])
SAIDA.mkdir(parents=True, exist_ok=True)
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")
dados = AQUI / "_dados" / "girar"
dados.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(dados)
os.environ["TEMP"] = os.environ["TMP"] = tempfile.mkdtemp(prefix="t-", dir=dados)
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)
try:
    import ctypes
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x40)
except Exception:  # noqa: BLE001
    pass

from PySide6.QtCore import QPoint  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir(exist_ok=True)
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])
from ui.janela_principal import JanelaPrincipal  # noqa: E402
from ui.widgets.editor_selecao import FERRAMENTA_RETANGULO  # noqa: E402
from ui.widgets.paineis import PAINEL_PROPRIEDADES  # noqa: E402
from ui.widgets.trilha_agrupada import FERRAMENTA_CORTAR, FERRAMENTA_ENDIREITAR  # noqa: E402

info: dict = {}


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def caixa(widget, janela) -> list[int]:
    p = widget.mapTo(janela, QPoint(0, 0))
    return [p.x(), p.y(), p.x() + widget.width(), p.y() + widget.height()]


janela = JanelaPrincipal()
janela.resize(1600, 1000)
janela.show()
janela.abrir_livro(LIVRO)
assentar(2)
c = janela.tela_conferir
c.ir_para_pagina(5)                       # página 6
c.paineis.abrir(PAINEL_PROPRIEDADES)
assentar(6)
for chave, ferramenta in (("cortar", FERRAMENTA_CORTAR), ("endireitar", FERRAMENTA_ENDIREITAR),
                          ("retangulo", FERRAMENTA_RETANGULO)):
    c.escolher_ferramenta(ferramenta)
    c.paineis.abrir(PAINEL_PROPRIEDADES)
    assentar(5)
    janela.grab().save(str(SAIDA / f"c-janela-{chave}.png"))
    info[chave] = {"bloco": caixa(c.barra_girar, janela), "canto": caixa(c.girar_do_canto, janela),
                   "trilha": caixa(c.trilha, janela) if hasattr(c, "trilha") else None,
                   "painel": caixa(c.paineis, janela), "bloco_visivel": c.barra_girar.isVisible(),
                   "canto_visivel": c.girar_do_canto.isVisible(),
                   "rotulo": c.barra_girar.rotulo.text()}
    print(chave, info[chave], flush=True)
c.barra_girar.grab().save(str(SAIDA / "c-bloco.png"))
c.girar_do_canto.grab().save(str(SAIDA / "c-canto.png"))
info["trilha_atributos"] = [n for n in dir(c) if "trilha" in n.lower()]
(SAIDA / "info-girar.json").write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
if janela.previas is not None:
    janela.previas.parar()
janela.close()
print("pronto", flush=True)
