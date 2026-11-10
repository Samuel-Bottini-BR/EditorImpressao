"""Ajudantes das provas das 4 perguntas da revisão do código (10/11/2026).

O programa roda SEM janela na tela: estes scripts rodam como testes do pytest, com o conftest dos
testes (QT_QPA_PLATFORM=offscreen: o Qt desenha só na memória; LOCALAPPDATA de mentira, dentro de
saida_teste/). Prioridade baixa (o PC tem outros agentes trabalhando). Nenhuma linha do programa
nem dos testes muda: só se chamam as funções que os botões chamam.

Uso (no worktree com o código da versão de teste, ramo obra-2026-10-26):
    set PROVAS_PDF=<cópia do livro>       (nunca o original)
    set PROVAS_SAIDA=<pasta das fotos cruas>
    python -m pytest -p tests.conftest <gerar_pN.py> -q -s
"""
from __future__ import annotations

import copy
import ctypes
import json
import os
import time
from pathlib import Path

# prioridade baixa (BELOW_NORMAL_PRIORITY_CLASS) para não travar o PC do Samuel
try:
    ctypes.windll.kernel32.SetPriorityClass(ctypes.windll.kernel32.GetCurrentProcess(), 0x4000)
except Exception:  # noqa: BLE001 - fora do Windows, segue sem trocar
    pass


def esperar(segundos: float) -> None:
    from PySide6.QtWidgets import QApplication

    fim = time.time() + segundos
    while time.time() < fim:
        QApplication.processEvents()
        time.sleep(0.05)


def esperar_previa(tela, limite: float = 60.0) -> None:
    esperar(0.5)
    t0 = time.time()
    while time.time() - t0 < limite:
        vis = getattr(tela, "visualizadores", {}).get(tela.aba_atual) or tela.area_imagem.currentWidget()
        if getattr(vis, "_pixmap", 1) is not None and not getattr(vis, "carregando", False):
            break
        esperar(0.2)
    esperar(1.5)


def esperar_editor(tela, limite: float = 60.0) -> None:
    """Espera a página chegar ao editor do Marcar."""
    t0 = time.time()
    while time.time() - t0 < limite:
        ed = tela.editor_selecao
        if ed._pixmap is not None and not ed._pixmap.isNull():
            break
        esperar(0.2)
    esperar(1.5)


def saida() -> Path:
    pasta = Path(os.environ["PROVAS_SAIDA"])
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def abrir(janela, largura: int = 1400, altura: int = 820):
    pdf = Path(os.environ["PROVAS_PDF"])
    janela.resize(largura, altura)
    janela.show()                                   # offscreen: desenhado só na memória
    janela.abrir_livro(str(pdf))
    esperar(2.0)
    return janela.tela_conferir, janela.projeto


def pdf_das_paginas(projeto, paginas: list[int], pasta: Path, nome: str, dpi: int = 60) -> list[str]:
    """O PDF que sai (core/pipeline.processar), só com `paginas` (as outras tiradas numa CÓPIA do
    projeto); cada página vira um PNG. Devolve os nomes, na ordem."""
    import fitz

    from core import pipeline

    copia = copy.deepcopy(projeto)
    for pg in copia.paginas:
        if pg.indice not in paginas:
            pg.apagada = True
    copia.caminho_saida = str(pasta / f"_{nome}.pdf")
    caminho = pipeline.processar(copia)
    nomes = []
    with fitz.open(caminho) as doc:
        for n, pagina in enumerate(doc):
            png = pasta / f"pdf-{nome}-{n + 1}.png"
            pagina.get_pixmap(dpi=dpi).save(str(png))
            nomes.append(png.name)
    Path(caminho).unlink(missing_ok=True)
    return nomes


def gravar_estado(nome: str, estado: dict) -> None:
    (saida() / f"estado-{nome}.json").write_text(
        json.dumps(estado, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


def ctrl_z(tela) -> None:
    from PySide6.QtCore import QEvent, Qt
    from PySide6.QtGui import QKeyEvent

    assert tela.tratar_tecla(QKeyEvent(QEvent.KeyPress, Qt.Key_Z, Qt.ControlModifier))
    esperar(1.0)
