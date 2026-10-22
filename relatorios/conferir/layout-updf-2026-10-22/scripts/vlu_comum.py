"""Montagem comum do verificador (livro aberto e tela cheia, 22/10/2026).

O programa de verdade (JanelaPrincipal) de uma worktree (argv: --codigo <pasta>), com
pasta de dados e de projetos próprias dentro dela (saida_teste/vlu_trab), janela fora da
tela, sem roubar o foco. Cliques por mensagens nativas do Windows (PostMessage no hwnd)."""
import ctypes
import os
import shutil
import sys
import time
from pathlib import Path

CODIGO = Path(sys.argv[sys.argv.index("--codigo") + 1]) if "--codigo" in sys.argv else Path(
    r"D:\programas\EditorImpressao\.claude\worktrees\layout-4a7")
TRAB = CODIGO / "saida_teste" / "vlu_trab"
if TRAB.exists():
    shutil.rmtree(TRAB)          # só a pasta que este script cria
(TRAB / "dados").mkdir(parents=True)
(TRAB / "tmp").mkdir()
os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(TRAB / "tmp")
sys.path.insert(0, str(CODIGO))
os.chdir(CODIGO)

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")

from PySide6.QtCore import QPoint, Qt  # noqa: E402
from PySide6.QtGui import QGuiApplication, QImage  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

app = QApplication.instance() or QApplication(sys.argv)

import projetos  # noqa: E402

(TRAB / "projetos").mkdir()
projetos.pasta_dos_projetos = lambda: TRAB / "projetos"

from ui.janela_principal import JanelaPrincipal  # noqa: E402

import numpy as np  # noqa: E402

user32 = ctypes.windll.user32
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_MOUSEWHEEL = 0x0200, 0x0201, 0x0202, 0x020A
MK_LBUTTON = 0x0001
RESULTADOS: list[tuple[bool, str]] = []
LONGE = -20000      # fora da tela, e cabe num inteiro de 16 bits mesmo a 125%


def copiar(nome_no_acervo: str, nome: str) -> Path:
    destino = TRAB / nome
    shutil.copy2(ACERVO / nome_no_acervo, destino)     # o original nunca é aberto
    return destino


def esperar(segundos: float) -> None:
    fim = time.time() + segundos
    while time.time() < fim:
        app.processEvents()
        time.sleep(0.01)


def esperar_ate(condicao, maximo: float, passo: float = 0.2) -> float:
    inicio = time.time()
    while time.time() - inicio < maximo:
        app.processEvents()
        try:
            if condicao():
                return time.time() - inicio
        except Exception:  # noqa: BLE001
            pass
        time.sleep(passo)
    return -1.0


def conferir(certo, frase: str) -> bool:
    RESULTADOS.append((bool(certo), frase))
    print(("  ok      " if certo else "  FALHOU  ") + frase, flush=True)
    return bool(certo)


def esconder(janela) -> None:
    janela.move(LONGE, LONGE)


def nova_janela(largura=1280, altura=657) -> JanelaPrincipal:
    janela = JanelaPrincipal()
    janela.setAttribute(Qt.WA_ShowWithoutActivating)
    esconder(janela)
    janela.resize(largura, altura)
    janela.show()
    esconder(janela)
    esperar(1)
    return janela


def tamanho_maximizada(janela) -> tuple[int, int]:
    """O tamanho da área de dentro da janela maximizada (pontos), pela tela de verdade."""
    livre = QGuiApplication.primaryScreen().availableGeometry()
    borda_h = janela.frameGeometry().height() - janela.geometry().height()
    return livre.width(), livre.height() - max(0, borda_h - 8)


def _lparam(janela, ponto: QPoint) -> int:
    escala = janela.devicePixelRatioF()
    x, y = round(ponto.x() * escala), round(ponto.y() * escala)
    return ((y & 0xFFFF) << 16) | (x & 0xFFFF)


def clique_nativo(janela, widget, ponto: QPoint | None = None) -> None:
    alvo = widget.mapTo(janela, ponto if ponto is not None else widget.rect().center())
    hwnd, lp = int(janela.winId()), _lparam(janela, alvo)
    user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, lp)
    esperar(0.15)
    user32.PostMessageW(hwnd, WM_LBUTTONDOWN, MK_LBUTTON, lp)
    esperar(0.15)
    user32.PostMessageW(hwnd, WM_LBUTTONUP, 0, lp)
    esperar(0.6)


def roda_nativa(janela, widget, delta: int) -> None:
    """WM_MOUSEWHEEL por PostMessage: as coordenadas são da TELA (pixels)."""
    centro = widget.mapToGlobal(widget.rect().center())
    escala = janela.devicePixelRatioF()
    x, y = round(centro.x() * escala), round(centro.y() * escala)
    lp = ((y & 0xFFFF) << 16) | (x & 0xFFFF)
    wp = ((delta & 0xFFFF) << 16)
    hwnd = int(janela.winId())
    user32.PostMessageW(hwnd, WM_MOUSEMOVE, 0, _lparam(janela, widget.mapTo(janela, widget.rect().center())))
    esperar(0.1)
    user32.PostMessageW(hwnd, WM_MOUSEWHEEL, wp, lp)
    esperar(0.5)


def em_numpy(pix) -> np.ndarray:
    img = pix.toImage().convertToFormat(QImage.Format_RGB888)
    d = np.frombuffer(img.constBits(), np.uint8, count=img.bytesPerLine() * img.height())
    return d.reshape(img.height(), img.bytesPerLine())[:, :img.width() * 3].reshape(
        img.height(), img.width(), 3).copy()


def memoria_mb() -> float:
    import psutil
    p = psutil.Process()
    total = p.memory_info().rss
    for filho in p.children(recursive=True):
        try:
            total += filho.memory_info().rss
        except Exception:  # noqa: BLE001
            pass
    return total / 2**20
