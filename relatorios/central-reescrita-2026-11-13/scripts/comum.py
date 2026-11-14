"""Base dos prints novos da reescrita da Central (13/11/2026), sem janela na tela do Samuel.

Cópia adaptada de relatorios/provas-central-2026-11-13/scripts/comum.py:
- QT_QPA_PLATFORM=offscreen com uma tela de 1600 x 821 pontos a 125% (= 1280 x 657, o notebook
  do Kaique); fontes do Windows (QT_QPA_FONTDIR).
- LOCALAPPDATA, APPDATA, TEMP e a pasta dos projetos numa pasta própria
  (<worktree>/_tmp/dados-<nome>), nunca a do Samuel.
- Prioridade baixa do processo.
- Prints por widget.grab().

O programa roda da worktree `.claude/worktrees/central-reescrita` (ramo obra-2026-10-26, só leitura:
nenhuma linha do programa muda). Os livros são CÓPIAS em <worktree>/_tmp/livros/.
"""
from __future__ import annotations

import ctypes
import os
import shutil
import sys
import time
from pathlib import Path

RAIZ = Path(r"D:\programas\EditorImpressao\.claude\worktrees\central-reescrita")
LIVROS = RAIZ / "_tmp" / "livros"
CRU = Path(__file__).resolve().parent.parent / "cru"
TRAB: Path | None = None
app = None


def preparar(nome: str, limpar: bool = True):
    global TRAB, app
    TRAB = RAIZ / "_tmp" / f"dados-{nome}"
    if limpar and TRAB.exists():
        shutil.rmtree(TRAB)           # só a pasta de dados deste script (criada por ele)
    for sub in ("dados", "projetos", "temp"):
        (TRAB / sub).mkdir(parents=True, exist_ok=True)
    os.environ["QT_QPA_PLATFORM"] = "offscreen:configfile=_tmp/tela-kaique.json"
    os.environ["QT_QPA_FONTDIR"] = "C:/Windows/Fonts"
    os.environ["QT_SCALE_FACTOR"] = "1.25"
    os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
    os.environ["APPDATA"] = str(TRAB / "dados")
    os.environ["TEMP"] = os.environ["TMP"] = str(TRAB / "temp")
    try:
        k = ctypes.windll.kernel32
        k.SetPriorityClass(k.GetCurrentProcess(), 0x00004000)   # BELOW_NORMAL
    except Exception:
        pass
    os.chdir(RAIZ)
    sys.path.insert(0, str(RAIZ))
    from PySide6.QtCore import Qt
    from PySide6.QtWidgets import QApplication

    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication.instance() or QApplication(sys.argv)
    app.setApplicationName("Editor de Impressão")
    import projetos

    projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
    return app


def esperar(seg: float) -> None:
    fim = time.monotonic() + seg
    while time.monotonic() < fim:
        app.processEvents()
        time.sleep(0.01)


def ate(condicao, limite: float = 300.0, passo: float = 0.2) -> float:
    t = time.monotonic()
    while time.monotonic() - t < limite:
        app.processEvents()
        try:
            if condicao():
                return round(time.monotonic() - t, 1)
        except Exception:
            pass
        esperar(passo)
    return -1.0


def nova_janela(largura: int = 1280, altura: int = 657):
    from ui.janela_principal import JanelaPrincipal

    j = JanelaPrincipal()
    j.resize(largura, altura)
    j.move(0, 0)
    j.show()
    esperar(0.5)
    return j


def esperar_tela(j, limite: float = 600.0) -> float:
    from ui.janela_principal import CONFERIR

    s = ate(lambda: j.telas.currentIndex() == CONFERIR and j.tela_conferir._pronta(), limite)
    esperar(1.5)
    return s


def esperar_previas(tela, indices, limite: float = 240.0) -> float:
    s = ate(lambda: all(tela.previas.ja_pronta(k, tela._dpi_atual) is not None for k in indices), limite)
    esperar(3.0)
    return s


def foto(widget, destino: Path) -> Path:
    esperar(0.3)
    destino.parent.mkdir(parents=True, exist_ok=True)
    widget.grab().save(str(destino))
    return destino


def fechar(j) -> None:
    try:
        j._fechar_a_janela_do_automatico()
    except Exception:
        pass
    try:
        if j.previas is not None:
            j.previas.parar()
    except Exception:
        pass
    j.close()
    esperar(0.5)
