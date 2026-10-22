"""Copiada do verificador vlm22 para o tc23 (23/10/2026), sem o apagar da pasta.
Base do verificador vlm22 (22/10/2026): abre o programa de verdade (JanelaPrincipal) de
uma worktree, fora da tela, com dados e projetos numa pasta de trabalho própria; cliques e
teclas por mensagens nativas do Windows (PostMessage para o hwnd); prints por PrintWindow
(PW_RENDERFULLCONTENT), não pelo grab do Qt; fecha com WM_CLOSE.

Uso: import base; base.preparar(worktree, trabalho)  (antes de importar ui)."""
import ctypes
import ctypes.wintypes as wt
import os
import shutil
import sys
import time
from pathlib import Path

ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32
WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP = 0x0200, 0x0201, 0x0202
WM_KEYDOWN, WM_KEYUP, WM_CHAR, WM_CLOSE = 0x0100, 0x0101, 0x0102, 0x0010
MK_LBUTTON = 1
RES: list = []
app = None
TRAB: Path = None


def preparar(worktree: str, trabalho: str, limpar: bool = True):
    """Aponta dados/TEMP para `trabalho` e põe a worktree no caminho do Python."""
    global app, TRAB
    TRAB = Path(trabalho)
    # tc23: nunca apaga nada (regra do Samuel); cada rodada usa uma pasta nova
    if limpar and TRAB.exists() and any(TRAB.iterdir()):
        raise SystemExit(f"pasta de trabalho já existe e não está vazia: {TRAB}")
    (TRAB / "dados").mkdir(parents=True, exist_ok=True)
    (TRAB / "projetos").mkdir(exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
    os.environ["TEMP"] = os.environ["TMP"] = str(TRAB)
    os.chdir(worktree)
    sys.path.insert(0, worktree)
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    _por_fora_da_tela()
    import projetos
    projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
    return app


_FILTRO = None


def _por_fora_da_tela():
    """Toda janela que o programa abre por cima (caixa de aviso, diálogo, menu) vai para fora
    da tela ANTES de aparecer: o Qt puxa diálogo e menu para dentro da tela do Samuel."""
    global _FILTRO
    from PySide6.QtCore import QEvent, QObject

    class Filtro(QObject):
        def eventFilter(self, obj, ev):  # noqa: N802
            if ev.type() == QEvent.Show and hasattr(obj, "isWindow") and obj.isWindow():
                g = obj.geometry()
                if g.x() > -20000:
                    obj.move(-31000 + (g.x() % 1000), -31000 + (g.y() % 1000))
                    print(f"  (pus fora da tela: {type(obj).__name__} que ia abrir em {g.x()},{g.y()})", flush=True)
            return False
    _FILTRO = Filtro()
    app.installEventFilter(_FILTRO)


def copia(nome_no_acervo: str, nome: str) -> Path:
    destino = TRAB / nome
    if not destino.exists():
        shutil.copy2(ACERVO / nome_no_acervo, destino)    # o original nunca é aberto
    return destino


def esperar(seg: float):
    fim = time.time() + seg
    while time.time() < fim:
        app.processEvents()
        time.sleep(0.01)


def conferir(ok, frase):
    RES.append((bool(ok), frase))
    print(("  ok      " if ok else "  FALHOU  ") + frase, flush=True)
    return bool(ok)


def nova_janela(largura=1280, altura=657):
    from PySide6.QtCore import Qt
    from ui.janela_principal import JanelaPrincipal
    j = JanelaPrincipal()
    j.setAttribute(Qt.WA_ShowWithoutActivating)
    j.move(-32000, -32000)
    j.resize(largura, altura)
    j.show()
    j.move(-32000, -32000)
    esperar(1)
    return j


def _lp(janela, p):
    e = janela.devicePixelRatioF()
    x, y = round(p.x() * e), round(p.y() * e)
    return (y << 16) | (x & 0xFFFF)


def clique(janela, widget, ponto=None, duplo=False):
    """Botão esquerdo por mensagens do Windows, no meio do widget (ou no ponto)."""
    alvo = widget.mapTo(janela, ponto if ponto is not None else widget.rect().center())
    h, lp = int(janela.winId()), _lp(janela, alvo)
    user32.PostMessageW(h, WM_MOUSEMOVE, 0, lp); esperar(0.15)
    user32.PostMessageW(h, WM_LBUTTONDOWN, MK_LBUTTON, lp); esperar(0.1)
    user32.PostMessageW(h, WM_LBUTTONUP, 0, lp); esperar(0.6)
    if duplo:
        user32.PostMessageW(h, 0x0203, MK_LBUTTON, lp); esperar(0.1)
        user32.PostMessageW(h, WM_LBUTTONUP, 0, lp); esperar(0.6)


def arrastar(janela, widget, de, para, passos=12):
    from PySide6.QtCore import QPoint
    h = int(janela.winId())
    a, b = widget.mapTo(janela, de), widget.mapTo(janela, para)
    user32.PostMessageW(h, WM_MOUSEMOVE, 0, _lp(janela, a)); esperar(0.15)
    user32.PostMessageW(h, WM_LBUTTONDOWN, MK_LBUTTON, _lp(janela, a)); esperar(0.15)
    for k in range(1, passos + 1):
        m = QPoint(round(a.x() + (b.x() - a.x()) * k / passos), round(a.y() + (b.y() - a.y()) * k / passos))
        user32.PostMessageW(h, WM_MOUSEMOVE, MK_LBUTTON, _lp(janela, m)); esperar(0.06)
    user32.PostMessageW(h, WM_LBUTTONUP, 0, _lp(janela, b)); esperar(1.0)


def digitar(janela, texto, enter=True):
    """Teclas por mensagens do Windows (WM_KEYDOWN/UP; o laço do Qt traduz em WM_CHAR, então
    não mandar WM_CHAR junto, senão sai dobrado) para a janela (vão ao widget com foco)."""
    h = int(janela.winId())
    for ch in texto:
        vk = user32.VkKeyScanW(ord(ch)) & 0xFF
        user32.PostMessageW(h, WM_KEYDOWN, vk, 1); esperar(0.03)
        user32.PostMessageW(h, WM_KEYUP, vk, 0xC0000001); esperar(0.05)
    if enter:
        user32.PostMessageW(h, WM_KEYDOWN, 0x0D, 1); esperar(0.03)
        user32.PostMessageW(h, WM_KEYUP, 0x0D, 0xC0000001)
    esperar(0.8)


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


def print_window(widget, destino: Path, so_cliente=True):
    """Print do hwnd pelo Windows (PrintWindow, PW_RENDERFULLCONTENT), em pixels de verdade."""
    from PIL import Image
    esperar(0.3)
    h = int(widget.winId())
    r = wt.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    w, a = r.right - r.left, r.bottom - r.top
    dc = user32.GetWindowDC(h)
    mdc = gdi32.CreateCompatibleDC(dc)
    bmp = gdi32.CreateCompatibleBitmap(dc, w, a)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(h, mdc, 2)
    bi = BITMAPINFOHEADER()
    bi.biSize = ctypes.sizeof(bi); bi.biWidth = w; bi.biHeight = -a; bi.biPlanes = 1; bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * a * 4)
    gdi32.GetDIBits(mdc, bmp, 0, a, buf, ctypes.byref(bi), 0)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(h, dc)
    img = Image.frombuffer("RGBA", (w, a), buf, "raw", "BGRA", 0, 1).convert("RGB")
    if so_cliente:
        c = wt.RECT(); user32.GetClientRect(h, ctypes.byref(c))
        p = wt.POINT(0, 0); user32.ClientToScreen(h, ctypes.byref(p))
        x0, y0 = p.x - r.left, p.y - r.top
        img = img.crop((x0, y0, x0 + c.right, y0 + c.bottom))
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino)
    print(f"  print {destino.name} {img.size}", flush=True)
    return img


def fechar(janela):
    user32.PostMessageW(int(janela.winId()), WM_CLOSE, 0, 0)
    esperar(2)
    conferir(not janela.isVisible(), "WM_CLOSE fechou a janela")


def gravar_resultados(destino: Path):
    falhas = [f for ok, f in RES if not ok]
    texto = "\n".join(("ok   " if ok else "FALHOU ") + f for ok, f in RES)
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "conferencias.txt").write_text(texto + f"\n{len(RES) - len(falhas)} de {len(RES)}\n", encoding="utf-8")
    print(f"\n{len(RES) - len(falhas)} de {len(RES)} certas", flush=True)


def tecla(janela, vk, char=None, vezes=1):
    h = int(janela.winId())
    for _ in range(vezes):
        user32.PostMessageW(h, WM_KEYDOWN, vk, 1); esperar(0.03)
        user32.PostMessageW(h, WM_KEYUP, vk, 0xC0000001); esperar(0.05)
    esperar(0.3)
