"""Captura, SEM JANELA NA TELA, as imagens da pergunta do D-646 (o Automático traz o fundo de
volta), no programa de hoje (o defeito não foi mexido: depende da pergunta ao Samuel).

    python capturar_fundo.py <raiz do código> <pasta de saída> <cópia do Siebmacher (10 páginas)>

O caminho do teste como o Kaique de 07/11: abrir o livro, "Sim, tirar o fundo" na pergunta,
rodar o Automático do jeito que ele abre ("Limpar a folha" em Original, mais Endireitar e Cortar
as bordas, os de fábrica). As páginas são desenhadas pelo mesmo caminho do PDF
(core.pipeline.renderizar_pagina), antes e depois do Automático. LOCALAPPDATA e projetos à
parte; só uma CÓPIA do livro.
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
os.environ.setdefault("QT_QPA_FONTDIR", "C:/Windows/Fonts")   # as letras da tela, sem janela
dados = Path(tempfile.mkdtemp(prefix="graves-fundo-"))
os.environ["LOCALAPPDATA"] = str(dados / "dados")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)

import cv2  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

import projetos  # noqa: E402

(dados / "projetos").mkdir()
projetos.pasta_dos_projetos = lambda: dados / "projetos"
app = QApplication.instance() or QApplication([])

from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import renderizar_pagina  # noqa: E402
from core import automatico as A  # noqa: E402
from ui.janela_principal import JanelaPrincipal  # noqa: E402

PAGINAS = [2, 3, 4, 5]


def assentar(segundos: float) -> None:
    fim = time.monotonic() + segundos
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.02)


def desenhar(janela, nome: str) -> None:
    doc = abrir_pdf(LIVRO)
    try:
        for i in PAGINAS:
            pagina = janela.projeto.paginas[i]
            img, _ = renderizar_pagina(doc, janela.projeto, pagina, dpi=50)
            cv2.imwrite(str(SAIDA / f"{nome}-{i + 1}.png"), cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                        if img.ndim == 3 else img)
            print(nome, i + 1, pagina.filtro)
    finally:
        doc.close()


janela = JanelaPrincipal()
janela.abrir_livro(LIVRO)
assentar(0.5)
janela._resposta_do_aviso_do_fundo(janela.resumo.pasta, True)     # "Sim, tirar o fundo"
if janela.aviso_do_fundo is not None:
    janela.aviso_do_fundo.done(0)
assentar(0.5)
desenhar(janela, "com-o-fundo-tirado")
# o Automático como ele abre (receita "De fábrica"): Endireitar, Cortar as bordas e "Limpar a
# folha" em Original, no livro todo, pulando as páginas mexidas à mão (o de fábrica)
pedido = A.Pedido(etapas=[A.ENDIREITAR, A.CORTAR, A.LIMPAR],
                  opcoes={"filtro_padrao": ORIGINAL}, pular_mexidas=True)
janela.rodar_o_automatico(pedido=pedido, esperar=True, perguntar=False)
assentar(1)
desenhar(janela, "depois-do-automatico")
if janela.previas is not None:
    janela.previas.parar()
janela.close()
print("pronto", SAIDA)
