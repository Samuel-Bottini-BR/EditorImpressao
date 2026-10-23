"""Base do verificador vlm22 (22/10/2026): abre o programa de verdade (JanelaPrincipal) de
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
    if limpar and TRAB.exists():
        shutil.rmtree(TRAB)      # só a pasta de trabalho deste script, no scratchpad
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
    if w <= 0 or a <= 0:
        print(f"  (janela sem tamanho para {destino.name}: visível={widget.isVisible()} "
              f"estado={int(widget.windowState().value) if hasattr(widget.windowState(), 'value') else widget.windowState()} "
              f"geometria={widget.geometry()}; tento de novo)", flush=True)
        widget.showNormal(); widget.move(-32000, -32000); esperar(1.5)
        user32.GetWindowRect(h, ctypes.byref(r))
        w, a = r.right - r.left, r.bottom - r.top
        if w <= 0 or a <= 0:
            print(f"  (sem print: {destino.name})", flush=True)
            return None
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


# --- acrescentado pelo verificador do mapa (23/10/2026) ---------------------------------------

def textos(raiz, so_visiveis=True):
    """Lista o que está escrito na tela dentro de `raiz`: cada botão, caixinha, rótulo, lista
    e campo visível, com onde fica (x, y em pontos na janela), se está ligado e o balão."""
    from PySide6.QtWidgets import (QAbstractButton, QCheckBox, QComboBox, QLabel, QLineEdit,
                                   QRadioButton, QSlider, QSpinBox, QWidget)
    linhas = []
    janela = raiz.window()
    for w in [raiz] + raiz.findChildren(QWidget):
        if so_visiveis and not w.isVisibleTo(janela):
            continue
        tipo = None
        texto = ""
        if isinstance(w, QCheckBox):
            tipo, texto = "caixinha", w.text()
        elif isinstance(w, QRadioButton):
            tipo, texto = "bolinha", w.text()
        elif isinstance(w, QAbstractButton):
            tipo, texto = "botão", w.text()
        elif isinstance(w, QLabel):
            tipo, texto = "texto", w.text()
        elif isinstance(w, QComboBox):
            tipo, texto = "lista", w.currentText() + "  [" + " | ".join(w.itemText(i) for i in range(w.count())) + "]"
        elif isinstance(w, QLineEdit):
            tipo, texto = "campo", w.text() or ("(" + w.placeholderText() + ")")
        elif isinstance(w, (QSlider, QSpinBox)):
            tipo, texto = "número", str(w.value())
        if tipo is None:
            continue
        if not texto and not w.toolTip() and tipo == "texto":
            continue
        p = w.mapTo(janela, w.rect().topLeft())
        estado = []
        if not w.isEnabled():
            estado.append("CINZA")
        if isinstance(w, QAbstractButton) and w.isCheckable():
            estado.append("marcado" if w.isChecked() else "desmarcado")
        dica = w.toolTip().replace("\n", " ")
        linhas.append(f"{tipo:8} ({p.x():4},{p.y():4} {w.width()}x{w.height()}) "
                      f"{' '.join(estado):18} {texto!r}" + (f"  · balão: {dica!r}" if dica else ""))
    return linhas


def gravar_textos(raiz, destino: Path, titulo=""):
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "a", encoding="utf-8") as f:
        f.write(f"\n===== {titulo} =====\n")
        f.write("\n".join(textos(raiz)) + "\n")


def acoes_do_menu(menu, nivel=0):
    """Os itens de um QMenu (e dos submenus), como aparecem: texto, atalho, cinza, marcado."""
    linhas = []
    for a in menu.actions():
        if a.isSeparator():
            linhas.append("  " * nivel + "----")
            continue
        if not a.isVisible():
            continue
        t = a.text().replace("&", "")
        extra = []
        if a.shortcut().toString():
            extra.append(a.shortcut().toString())
        if not a.isEnabled():
            extra.append("CINZA")
        if a.isCheckable():
            extra.append("marcado" if a.isChecked() else "desmarcado")
        linhas.append("  " * nivel + t + (f"   [{', '.join(extra)}]" if extra else ""))
        if a.menu() is not None:
            linhas += acoes_do_menu(a.menu(), nivel + 1)
    return linhas


def print_do_menu_que_abrir(nome, saida: Path, txt: Path, fechar=True, depois=None):
    """Quando um QMenu abrir (exec ou popup, já posto fora da tela pelo filtro), tira o print
    dele, lista os itens no `txt` e fecha. Chamar ANTES do clique que abre o menu."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication, QMenu
    tentativas = [0]

    def olhar():
        menus = [w for w in QApplication.topLevelWidgets() if isinstance(w, QMenu) and w.isVisible()]
        if not menus:
            tentativas[0] += 1
            if tentativas[0] < 40:
                QTimer.singleShot(150, olhar)
            else:
                print(f"  (nenhum menu abriu para {nome})", flush=True)
            return
        m = menus[-1]
        print_window(m, saida / f"{nome}.png", so_cliente=False)
        with open(txt, "a", encoding="utf-8") as f:
            f.write(f"\n===== menu {nome} =====\n" + "\n".join(acoes_do_menu(m)) + "\n")
        if depois:
            depois(m)
        if fechar:
            m.close()
    QTimer.singleShot(400, olhar)


def quando_abrir_janela(tipo, nome, saida: Path, txt: Path, depois=None, fechar=True, espera_ms=1500):
    """Para janelas que abrem com exec() (bloqueiam): quando uma janela visível do `tipo`
    aparecer, espera `espera_ms`, tira o print dela, grava os textos, chama `depois(janela)` e
    fecha (reject/close). Chamar ANTES do clique que a abre."""
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    tentativas = [0]

    def olhar():
        abertas = [w for w in QApplication.topLevelWidgets() if isinstance(w, tipo) and w.isVisible()]
        if not abertas:
            tentativas[0] += 1
            if tentativas[0] < 200:
                QTimer.singleShot(150, olhar)
            else:
                print(f"  (nenhuma janela {tipo.__name__} abriu para {nome})", flush=True)
            return
        w = abertas[-1]

        def agir():
            print_window(w, saida / f"{nome}.png", so_cliente=False)
            gravar_textos(w, txt, f"janela {nome} ({type(w).__name__}, título '{w.windowTitle()}')")
            if depois:
                depois(w)
            if fechar and w.isVisible():
                (w.reject if hasattr(w, "reject") else w.close)()
        QTimer.singleShot(espera_ms, agir)
    QTimer.singleShot(300, olhar)
