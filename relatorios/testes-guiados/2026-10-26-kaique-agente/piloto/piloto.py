"""Piloto do "teste do Kaique" (26/10/2026).

Abre o programa pelo main.py da worktree (sem ler o código dele), com a janela e tudo o que ela
abrir FORA da tela, dados/TEMP numa pasta de trabalho própria. Depois fica esperando comandos
num arquivo (fila/cmd.json) e responde em fila/res.json. Os comandos são só de "pessoa":
print, clique x y, duplo, direito, arrastar, mover (passar o mouse), rolar, tecla, digitar.
Coordenadas em pontos da janela de 1280x657 (a tela do notebook do Kaique).

Infra adaptada de relatorios/testes-guiados/livros/roteiros/base.py (ramo testes-livros-2026-10-23):
janela fora da tela, PrintWindow, PostMessage. Nada aqui procura botão pelo nome no código.

Uso:  python piloto.py <pasta_trabalho> <worktree>
"""
import ctypes
import ctypes.wintypes as wt
import json
import os
import runpy
import sys
import threading
import time
import traceback
from pathlib import Path

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32")
HWND = wt.HWND
user32.PostMessageW.argtypes = [HWND, wt.UINT, wt.WPARAM, wt.LPARAM]
user32.GetWindowRect.argtypes = [HWND, ctypes.POINTER(wt.RECT)]
user32.GetClientRect.argtypes = [HWND, ctypes.POINTER(wt.RECT)]
user32.ClientToScreen.argtypes = [HWND, ctypes.POINTER(wt.POINT)]
user32.GetWindowDC.argtypes = [HWND]
user32.GetWindowDC.restype = wt.HDC
user32.ReleaseDC.argtypes = [HWND, wt.HDC]
user32.PrintWindow.argtypes = [HWND, wt.HDC, wt.UINT]
user32.IsWindowVisible.argtypes = [HWND]
user32.GetWindowThreadProcessId.argtypes = [HWND, ctypes.POINTER(wt.DWORD)]
user32.GetClassNameW.argtypes = [HWND, wt.LPWSTR, ctypes.c_int]
user32.InternalGetWindowText.argtypes = [HWND, wt.LPWSTR, ctypes.c_int]
user32.SetWindowPos.argtypes = [HWND, HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wt.UINT]
user32.GetDpiForWindow.argtypes = [HWND]
user32.GetAncestor.argtypes = [HWND, wt.UINT]
user32.GetAncestor.restype = HWND
gdi32.CreateCompatibleDC.argtypes = [wt.HDC]
gdi32.CreateCompatibleDC.restype = wt.HDC
gdi32.CreateCompatibleBitmap.argtypes = [wt.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wt.HBITMAP
gdi32.SelectObject.argtypes = [wt.HDC, wt.HGDIOBJ]
gdi32.DeleteObject.argtypes = [wt.HGDIOBJ]
gdi32.DeleteDC.argtypes = [wt.HDC]
gdi32.GetDIBits.argtypes = [wt.HDC, wt.HBITMAP, wt.UINT, wt.UINT, ctypes.c_void_p, ctypes.c_void_p, wt.UINT]

WM_MOUSEMOVE, WM_LBUTTONDOWN, WM_LBUTTONUP, WM_LBUTTONDBLCLK = 0x0200, 0x0201, 0x0202, 0x0203
WM_RBUTTONDOWN, WM_RBUTTONUP, WM_MOUSEWHEEL = 0x0204, 0x0205, 0x020A
WM_KEYDOWN, WM_KEYUP, WM_CHAR, WM_CLOSE = 0x0100, 0x0101, 0x0102, 0x0010
MK_LBUTTON, MK_RBUTTON = 1, 2
LARG, ALT = 1280, 657
PID = os.getpid()
TRAB: Path = None
ULTIMO_PONTO = [640, 330]
LOG = None

TECLAS = {"enter": 0x0D, "esc": 0x1B, "tab": 0x09, "espaco": 0x20, "back": 0x08, "delete": 0x2E,
          "esquerda": 0x25, "cima": 0x26, "direita": 0x27, "baixo": 0x28, "pgup": 0x21, "pgdn": 0x22,
          "home": 0x24, "end": 0x23, "f1": 0x70, "f2": 0x71, "f3": 0x72, "f4": 0x73, "f5": 0x74,
          "f6": 0x75, "f7": 0x76, "f8": 0x77, "f9": 0x78, "f10": 0x79, "f11": 0x7A, "f12": 0x7B}


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    if LOG:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%H:%M:%S ") + s + "\n")


# ------------------------------------------------------------------ janelas do processo (Win32)
def janelas():
    """Janelas visíveis deste processo, de cima para baixo (ordem Z)."""
    achadas = []

    @ctypes.WINFUNCTYPE(wt.BOOL, HWND, wt.LPARAM)
    def cb(h, _):
        pid = wt.DWORD()
        user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
        if pid.value == PID and user32.IsWindowVisible(h):
            cls = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(h, cls, 256)
            tit = ctypes.create_unicode_buffer(512)
            user32.InternalGetWindowText(h, tit, 512)
            r = wt.RECT()
            user32.GetWindowRect(h, ctypes.byref(r))
            if r.right - r.left > 2 and r.bottom - r.top > 2:
                achadas.append({"hwnd": int(h or 0), "classe": cls.value, "titulo": tit.value,
                                "ret": [r.left, r.top, r.right - r.left, r.bottom - r.top]})
        return True
    user32.EnumWindows(cb, 0)
    return achadas


def principal():
    js = [j for j in janelas() if "ToolTip" not in j["classe"] and "Popup" not in j["classe"]]
    if not js:
        return None
    return max(js, key=lambda j: j["ret"][2] * j["ret"][3])


def escala(h):
    try:
        return user32.GetDpiForWindow(h) / 96.0
    except Exception:
        return 1.25


def alvo(qual):
    """'p' = janela principal; 't' = a de cima (diálogo/menu) que não é balão; número = índice."""
    js = janelas()
    if qual in (None, "t"):
        for j in js:
            if "ToolTip" not in j["classe"]:
                return j
        return None
    if qual == "p":
        return principal()
    if qual == "d":   # a janela de cima que não é menu/lista suspensa/balão (diálogo)
        for j in js:
            if "ToolTip" not in j["classe"] and "Popup" not in j["classe"]:
                return j
        return None
    if qual == "m":   # o menu/lista suspensa aberto
        for j in js:
            if "Popup" in j["classe"]:
                return j
        return None
    if str(qual).lstrip("-").isdigit():
        return js[int(qual)]
    for j in js:      # pedaço do título
        if str(qual).lower() in j["titulo"].lower():
            return j
    return None


def _lp(h, x, y):
    e = escala(h)
    X, Y = round(x * e), round(y * e)
    return (Y << 16) | (X & 0xFFFF)


def post(h, msg, wp, lp):
    user32.PostMessageW(h, msg, wp, lp)


# ------------------------------------------------------------------ prints
class BIH(ctypes.Structure):
    _fields_ = [("biSize", wt.DWORD), ("biWidth", wt.LONG), ("biHeight", wt.LONG), ("biPlanes", wt.WORD),
                ("biBitCount", wt.WORD), ("biCompression", wt.DWORD), ("biSizeImage", wt.DWORD),
                ("biXPelsPerMeter", wt.LONG), ("biYPelsPerMeter", wt.LONG), ("biClrUsed", wt.DWORD),
                ("biClrImportant", wt.DWORD)]


def captura(h, so_cliente=True):
    from PIL import Image
    r = wt.RECT()
    user32.GetWindowRect(h, ctypes.byref(r))
    w, a = r.right - r.left, r.bottom - r.top
    if w <= 0 or a <= 0:
        return None
    dc = user32.GetWindowDC(h)
    mdc = gdi32.CreateCompatibleDC(dc)
    bmp = gdi32.CreateCompatibleBitmap(dc, w, a)
    gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(h, mdc, 2)
    bi = BIH()
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
    e = escala(h)
    if abs(e - 1) > 0.01:
        img = img.resize((round(img.width / e), round(img.height / e)), Image.LANCZOS)
    return img


def tirar_print(nome):
    """Print da principal + de cada janela de cima (menu, diálogo, balão), e um 'junto' com as
    de cima coladas perto do último ponto clicado (para ver como a pessoa veria)."""
    from PIL import ImageDraw
    pasta = TRAB / "telas"
    pasta.mkdir(exist_ok=True)
    js = janelas()
    p = principal()
    saidas = []
    base = captura(p["hwnd"]) if p else None
    if base is not None:
        base.save(pasta / f"{nome}.png"); saidas.append(str(pasta / f"{nome}.png"))
    outras = [j for j in js if p is None or j["hwnd"] != p["hwnd"]]
    junto = base.copy() if base is not None else None
    for i, j in enumerate(reversed(outras)):
        im = captura(j["hwnd"], so_cliente=True)   # só a parte de dentro: as coordenadas dos cliques batem com o print
        if im is None:
            continue
        cam = pasta / f"{nome}_cima{len(outras) - 1 - i}.png"
        im.save(cam); saidas.append(str(cam))
        if junto is not None:
            if im.width > 500 or im.height > 300:   # diálogo: no meio
                x, y = (junto.width - im.width) // 2, (junto.height - im.height) // 2
            else:                                   # menu/balão: perto do último clique
                x, y = ULTIMO_PONTO[0], ULTIMO_PONTO[1] + 4
            x = max(0, min(x, junto.width - im.width)); y = max(0, min(y, junto.height - im.height))
            x, y = int(x), int(y)
            junto.paste(im, (x, y))
            ImageDraw.Draw(junto).rectangle([x - 1, y - 1, x + im.width, y + im.height], outline=(255, 0, 255))
    if outras and junto is not None:
        junto.save(pasta / f"{nome}_junto.png"); saidas.append(str(pasta / f"{nome}_junto.png"))
    return saidas, js


# ------------------------------------------------------------------ ações de "pessoa"
def clique(x, y, qual=None, duplo=False, direito=False):
    j = alvo(qual)
    h = j["hwnd"]
    lp = _lp(h, x, y)
    if j is principal():
        ULTIMO_PONTO[:] = [x, y]
    post(h, WM_MOUSEMOVE, 0, lp); time.sleep(0.12)
    if direito:
        post(h, WM_RBUTTONDOWN, MK_RBUTTON, lp); time.sleep(0.08)
        post(h, WM_RBUTTONUP, 0, lp)
        return j
    post(h, WM_LBUTTONDOWN, MK_LBUTTON, lp); time.sleep(0.08)
    post(h, WM_LBUTTONUP, 0, lp)
    if duplo:
        time.sleep(0.08)
        post(h, WM_LBUTTONDBLCLK, MK_LBUTTON, lp); time.sleep(0.08)
        post(h, WM_LBUTTONUP, 0, lp)
    return j


def arrastar(x1, y1, x2, y2, qual=None, passos=14):
    j = alvo(qual); h = j["hwnd"]
    post(h, WM_MOUSEMOVE, 0, _lp(h, x1, y1)); time.sleep(0.12)
    post(h, WM_LBUTTONDOWN, MK_LBUTTON, _lp(h, x1, y1)); time.sleep(0.12)
    for k in range(1, passos + 1):
        x = x1 + (x2 - x1) * k / passos; y = y1 + (y2 - y1) * k / passos
        post(h, WM_MOUSEMOVE, MK_LBUTTON, _lp(h, x, y)); time.sleep(0.05)
    post(h, WM_LBUTTONUP, 0, _lp(h, x2, y2))
    ULTIMO_PONTO[:] = [x2, y2]
    return j


def mover(x, y, qual=None):
    j = alvo(qual); h = j["hwnd"]
    post(h, WM_MOUSEMOVE, 0, _lp(h, x, y))
    ULTIMO_PONTO[:] = [x, y]
    return j


def rolar(x, y, n, qual=None):
    j = alvo(qual); h = j["hwnd"]
    e = escala(h)
    p = wt.POINT(round(x * e), round(y * e)); user32.ClientToScreen(h, ctypes.byref(p))
    post(h, WM_MOUSEMOVE, 0, _lp(h, x, y)); time.sleep(0.05)
    for _ in range(abs(int(n))):
        delta = (-120 if n > 0 else 120) & 0xFFFF   # n>0 = rolar para baixo
        post(h, WM_MOUSEWHEEL, delta << 16, ((p.y & 0xFFFF) << 16) | (p.x & 0xFFFF)); time.sleep(0.08)
    return j


def tecla(nome, vezes=1, qual=None):
    j = alvo(qual); h = j["hwnd"]
    vk = TECLAS[nome.lower()]
    for _ in range(vezes):
        post(h, WM_KEYDOWN, vk, 1); time.sleep(0.03)
        post(h, WM_KEYUP, vk, 0xC0000001); time.sleep(0.06)
    return j


def digitar(texto, qual=None):
    j = alvo(qual); h = j["hwnd"]
    for ch in texto:
        post(h, WM_CHAR, ord(ch), 1); time.sleep(0.03)
    return j


def fechar_janela(qual):
    j = alvo(qual)
    post(j["hwnd"], WM_CLOSE, 0, 0)
    return j


def executar(c):
    a = c["acao"]; q = c.get("alvo")
    if a == "clique":
        clique(c["x"], c["y"], q)
    elif a == "duplo":
        clique(c["x"], c["y"], q, duplo=True)
    elif a == "direito":
        clique(c["x"], c["y"], q, direito=True)
    elif a == "arrastar":
        arrastar(c["x"], c["y"], c["x2"], c["y2"], q)
    elif a == "mover":
        mover(c["x"], c["y"], q)
    elif a == "rolar":
        rolar(c["x"], c["y"], c["n"], q)
    elif a == "tecla":
        tecla(c["nome"], c.get("vezes", 1), q)
    elif a == "digitar":
        digitar(c["texto"], q)
    elif a == "fecharjanela":
        fechar_janela(q)
    elif a in ("print", "janelas", "esperar"):
        pass
    else:
        raise ValueError("ação desconhecida " + a)
    time.sleep(float(c.get("espera", 0.9)))
    res = {"ok": True, "janelas": janelas()}
    if c.get("print"):
        res["prints"], _ = tirar_print(c["print"])
    return res


def laco_de_comandos():
    fila = TRAB / "fila"
    fila.mkdir(exist_ok=True)
    cmd, resp = fila / "cmd.json", fila / "res.json"
    while True:
        try:
            if cmd.exists():
                c = json.loads(cmd.read_text(encoding="utf-8"))
                cmd.unlink()
                log("cmd", c)
                try:
                    r = executar(c)
                except Exception as e:
                    r = {"ok": False, "erro": repr(e), "tb": traceback.format_exc()}
                r["id"] = c.get("id")
                tmp = fila / "res.tmp"
                tmp.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
                os.replace(tmp, resp)
        except Exception as e:
            log("erro no laço", repr(e))
        time.sleep(0.05)


def guarda_win32():
    """Qualquer janela deste processo que apareça dentro da tela vai para fora (sem esperar o
    Qt; serve também para janela nativa do Windows)."""
    SWP = 0x0001 | 0x0004 | 0x0010 | 0x4000   # NOSIZE|NOZORDER|NOACTIVATE|ASYNCWINDOWPOS
    while True:
        try:
            for j in janelas():
                x, y = j["ret"][0], j["ret"][1]
                if x > -20000 and y > -20000:
                    user32.SetWindowPos(j["hwnd"], None, -31000 + abs(x) % 1000, -31000 + abs(y) % 1000, 0, 0, SWP)
                    log("guarda: pus fora da tela", j["classe"], j["titulo"], x, y)
        except Exception as e:
            log("erro guarda", repr(e))
        time.sleep(0.015)


# ------------------------------------------------------------------ dentro do Qt (só posição)
def preparar_qt():
    from PySide6 import QtWidgets
    from PySide6.QtCore import QCoreApplication, QEvent, QObject, Qt, QTimer

    QCoreApplication.setAttribute(Qt.AA_DontUseNativeDialogs, True)   # diálogo de arquivo do Qt (fica fora da tela)
    Original = QtWidgets.QApplication

    def tirar(obj):
        try:
            if isinstance(obj, QtWidgets.QMainWindow):
                if obj.windowState() & (Qt.WindowMaximized | Qt.WindowFullScreen):
                    obj.setWindowState(Qt.WindowNoState)
                if obj.width() != LARG or obj.height() != ALT:
                    obj.resize(LARG, ALT)
            g = obj.frameGeometry()
            if g.x() > -20000 and g.y() > -20000:
                if isinstance(obj, QtWidgets.QMainWindow):
                    obj.move(-32000, -32000)
                else:
                    obj.move(-31000 + abs(g.x()) % 1000, -31000 + abs(g.y()) % 1000)
        except RuntimeError:
            pass

    class Filtro(QObject):
        def eventFilter(self, obj, ev):  # noqa: N802
            t = ev.type()
            if t in (QEvent.Polish, QEvent.Show, QEvent.Move, QEvent.WindowStateChange) and \
                    isinstance(obj, QtWidgets.QWidget) and obj.isWindow():
                if t == QEvent.Polish:
                    obj.setAttribute(Qt.WA_ShowWithoutActivating, True)
                tirar(obj)
                QTimer.singleShot(0, lambda o=obj: tirar(o))
            return False

    class App(Original):
        def __init__(self, *a, **k):
            super().__init__(*a, **k)
            self._filtro_kaique = Filtro()
            self.installEventFilter(self._filtro_kaique)
            self._guarda = QTimer()
            self._guarda.timeout.connect(lambda: [tirar(w) for w in QtWidgets.QApplication.topLevelWidgets() if w.isVisible()])
            self._guarda.start(20)
            log("App do piloto criado")

    QtWidgets.QApplication = App


def main():
    global TRAB, LOG
    TRAB = Path(sys.argv[1]).resolve()
    wt_ = Path(sys.argv[2]).resolve()
    LOG = TRAB / "piloto.log"
    (TRAB / "dados").mkdir(parents=True, exist_ok=True)
    (TRAB / "projetos").mkdir(exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
    os.environ["TEMP"] = os.environ["TMP"] = str(TRAB)
    os.chdir(wt_)
    sys.path.insert(0, str(wt_))
    (TRAB / "pid.txt").write_text(str(PID))
    log("PID", PID)
    threading.Thread(target=guarda_win32, daemon=True).start()
    preparar_qt()
    import projetos   # mesmo isolamento que o base.py usa: projetos na pasta de trabalho
    projetos.pasta_dos_projetos = lambda: TRAB / "projetos"
    threading.Thread(target=laco_de_comandos, daemon=True).start()
    sys.argv = [str(wt_ / "main.py")]
    runpy.run_path(str(wt_ / "main.py"), run_name="__main__")
    log("programa terminou")


if __name__ == "__main__":
    main()
