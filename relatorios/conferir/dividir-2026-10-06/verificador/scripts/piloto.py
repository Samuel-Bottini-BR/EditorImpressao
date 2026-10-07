"""Piloto da janela real (verificador de tela, 02/10/2026). So ctypes.

Cliques e teclas: mensagens nativas do Windows (PostMessage) direto para o
hwnd da janela de teste. Nunca move o mouse nem usa o teclado de verdade do
Samuel. Para Ctrl/Shift/Alt: AttachThreadInput + SetKeyboardState so na fila
de entrada do processo de teste (nao a do Samuel), e devolve o estado depois.

Print: PrintWindow(PW_RENDERFULLCONTENT), recortado na moldura visivel
(DWMWA_EXTENDED_FRAME_BOUNDS), para nao pegar a borda invisivel do Windows 11.
"""
import ctypes
import ctypes.wintypes as W
import json
import os
import subprocess
import time
from pathlib import Path

AQUI = Path(__file__).parent
BASE = AQUI.parent
RAIZ = Path(r"D:\programas\EditorImpressao")
PYW = RAIZ / ".venv" / "Scripts" / "pythonw.exe"
DADOS = BASE / "dados_teste"
ESTADO = AQUI / "estado.json"
# verificador-2: o canal de comandos fica no C: (pasta de rascunho), longe do
# disco USB; quem le o canal dentro do programa e um fio de fundo (lancador2)
CANAL = Path(os.environ.get("VERIF_CANAL", r"C:\Users\fotog\AppData\Local\Temp\claude\d--programas\5c0a83a2-d2ec-4c63-b11e-6af7ca2c16b0\scratchpad\canal_dividir"))
CANAL.mkdir(parents=True, exist_ok=True)
VERIF_RAIZ = os.environ.get("VERIF_RAIZ", str(BASE / "trabalho" / "novo"))

ctypes.windll.shcore.SetProcessDpiAwareness(2)
u32 = ctypes.WinDLL("user32", use_last_error=True)
g32 = ctypes.WinDLL("gdi32")
k32 = ctypes.WinDLL("kernel32")
dwm = ctypes.WinDLL("dwmapi")
u32.PostMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
u32.SendMessageW.argtypes = [W.HWND, W.UINT, W.WPARAM, W.LPARAM]
u32.SendMessageW.restype = ctypes.c_ssize_t
u32.SetWindowPos.argtypes = [W.HWND, W.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, W.UINT]

ESCALA = u32.GetDpiForSystem() / 96.0
LOGICO = (1280, 657)  # area util do notebook do Kaique a 150%


# ---------------------------------------------------------------- processo
def iniciar(*args):
    env = dict(os.environ)
    env["LOCALAPPDATA"] = str(DADOS / "local")
    env["USERPROFILE"] = str(DADOS / "home")
    env["TEMP"] = env["TMP"] = str(BASE / "trabalho" / "tmp")  # C: quase cheio
    env["VERIF_CANAL"] = str(CANAL)
    env["VERIF_RAIZ"] = VERIF_RAIZ
    for velho in ("comando.txt", "sonda.json", "mapa.json", "paradas.log"):
        try:
            (CANAL / velho).unlink()
        except OSError:
            pass
    saida = open(CANAL / f"programa_{time.strftime('%H%M%S')}.log", "w", encoding="utf-8")
    p = subprocess.Popen([str(PYW), str(AQUI / "lancador2.py"), *args], cwd=str(AQUI), env=env,
                         stdout=saida, stderr=subprocess.STDOUT)
    ESTADO.write_text(json.dumps({"pid": p.pid}))
    for _ in range(600):
        time.sleep(0.2)
        try:
            return principal()
        except LookupError:
            pass
    raise RuntimeError("janela nao apareceu")


def pid():
    import psutil
    est = json.loads(ESTADO.read_text())
    if est.get("filho"):
        return est["filho"]
    lanc = est["pid"]
    try:
        filhos = psutil.Process(lanc).children()
    except psutil.NoSuchProcess:
        return lanc
    return filhos[0].pid if filhos else lanc


def vivo():
    h = k32.OpenProcess(0x1000, False, pid())
    if not h:
        return False
    code = W.DWORD(); k32.GetExitCodeProcess(h, ctypes.byref(code)); k32.CloseHandle(h)
    return code.value == 259


def janelas():
    achadas, alvo = [], pid()

    @ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
    def cada(h, _):
        p = W.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(p))
        if p.value == alvo and u32.IsWindowVisible(h):
            t = ctypes.create_unicode_buffer(256); u32.GetWindowTextW(h, t, 256)
            c = ctypes.create_unicode_buffer(256); u32.GetClassNameW(h, c, 256)
            r = W.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
            achadas.append((h, t.value, c.value, (r.left, r.top, r.right - r.left, r.bottom - r.top)))
        return True
    u32.EnumWindows(cada, 0)
    return achadas


def principal():
    for h, t, c, _ in janelas():
        if t == "Editor de Impressão" and c.endswith("QWindowIcon"):
            return h
    raise LookupError("janela principal nao achada")


def fechar():
    u32.PostMessageW(principal(), 0x10, 0, 0)
    for _ in range(150):
        time.sleep(0.1)
        if not vivo():
            return True
    return False


# ---------------------------------------------------------------- leitura
def _pedir(cmd, arquivo, espera=60.0):
    """Verificador-2: depois do tempo-limite o laco olha a resposta UMA
    ULTIMA VEZ (o do verificador-1 desistia sem olhar: falso "sem
    resposta"). Espera longa (60 s): janela parada de verdade aparece como
    resposta lenta (campo "lat", medido dentro do processo), nao como erro."""
    alvo = CANAL / arquivo
    for _ in range(100):
        try:
            if alvo.exists():
                alvo.unlink()
            break
        except PermissionError:
            time.sleep(0.01)
    tmp = CANAL / "comando.tmp"
    tmp.write_text(cmd, encoding="utf-8")
    for _ in range(50):
        try:
            os.replace(tmp, CANAL / "comando.txt")   # inteiro, de uma vez
            break
        except PermissionError:
            time.sleep(0.01)
    fim = time.time() + espera
    while True:
        ultima = time.time() >= fim
        if alvo.is_file():
            try:
                return json.loads(alvo.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                pass
        if ultima:
            break
        time.sleep(0.02)
    raise RuntimeError(f"sem resposta para {cmd!r} em {espera} s")


def mapa():
    return _pedir("mapa", "mapa.json")


def sonda(expr, com_lat=False, espera=60.0):
    r = _pedir("sonda " + expr, "sonda.json", espera)
    if not r["ok"]:
        raise RuntimeError(r["erro"])
    return (r["valor"], r["lat"]) if com_lat else r["valor"]


def paradas():
    """O que o vigia do lancador2 anotou: (inicio, duracao) e as pilhas."""
    f = CANAL / "paradas.log"
    return f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""


def matar():
    """TerminateProcess SO no processo de teste (o pid que este piloto abriu)."""
    h = k32.OpenProcess(0x0001 | 0x1000, False, pid())
    if not h:
        return False
    ok = k32.TerminateProcess(h, 9)
    k32.CloseHandle(h)
    return bool(ok)


def janela(titulo=None, classe=None, contem=False):
    for j in mapa():
        if titulo is not None and not ((titulo in j["titulo"]) if contem else j["titulo"] == titulo):
            continue
        if classe is not None and j["classe"] != classe:
            continue
        return j
    return None


def achar(texto, j=None, classe=None, exato=True, n=0):
    js = [j] if j else mapa()
    res = []
    for jj in js:
        for it in jj["itens"]:
            t = it["texto"] or ""
            if (t == texto if exato else texto in t) and (classe is None or it["classe"] == classe):
                res.append((jj, it))
    if len(res) <= n:
        raise LookupError(f"nao achei {texto!r} classe={classe}")
    return res[n]


# ---------------------------------------------------------------- mouse
def lp(x, y):
    return (int(y) << 16) | (int(x) & 0xFFFF)


def clicar_em(hwnd, x, y, duplo=False, botao="esq"):
    down, up, dbl, mk = (0x201, 0x202, 0x203, 1) if botao == "esq" else (0x204, 0x205, 0x206, 2)
    u32.PostMessageW(hwnd, 0x200, 0, lp(x, y)); time.sleep(0.05)
    u32.PostMessageW(hwnd, down, mk, lp(x, y)); time.sleep(0.05)
    u32.PostMessageW(hwnd, up, 0, lp(x, y))
    if duplo:
        time.sleep(0.05)
        u32.PostMessageW(hwnd, dbl, mk, lp(x, y)); time.sleep(0.05)
        u32.PostMessageW(hwnd, up, 0, lp(x, y))


def clicar(texto, titulo=None, classe=None, exato=True, n=0, dx=None, espera=0.7, duplo=False, botao="esq"):
    j = janela(titulo) if titulo else None
    j, it = achar(texto, j, classe, exato, n)
    x = it["x"] + (dx if dx is not None else it["w"] / 2)
    y = it["y"] + it["h"] / 2
    clicar_em(j["hwnd"], int(x), int(y), duplo=duplo, botao=botao)
    time.sleep(espera)
    return j, it


def arrastar_em(hwnd, x0, y0, x1, y1, passos=12):
    u32.PostMessageW(hwnd, 0x200, 0, lp(x0, y0)); time.sleep(0.1)
    u32.PostMessageW(hwnd, 0x201, 1, lp(x0, y0)); time.sleep(0.1)
    for i in range(1, passos + 1):
        x = x0 + (x1 - x0) * i / passos; y = y0 + (y1 - y0) * i / passos
        u32.PostMessageW(hwnd, 0x200, 1, lp(x, y)); time.sleep(0.04)
    time.sleep(0.1)
    u32.PostMessageW(hwnd, 0x202, 0, lp(x1, y1))


# ---------------------------------------------------------------- teclado
VK = {"ctrl": 0x11, "shift": 0x10, "alt": 0x12}
_EXT = {0x25, 0x26, 0x27, 0x28, 0x2D, 0x2E, 0x21, 0x22, 0x23, 0x24}


def _lp_tecla(vk, solta=False):
    scan = u32.MapVirtualKeyW(vk, 0)
    v = 1 | (scan << 16) | ((1 << 24) if vk in _EXT else 0)
    if solta:
        v |= 0xC0000000
    return v


def tecla(vk, hwnd=None, mods=()):
    hwnd = hwnd or principal()
    if isinstance(vk, str):
        vk = ord(vk.upper())
    if not mods:
        u32.PostMessageW(hwnd, 0x100, vk, _lp_tecla(vk)); time.sleep(0.05)
        u32.PostMessageW(hwnd, 0x101, vk, _lp_tecla(vk, True))
        return
    alvo = u32.GetWindowThreadProcessId(hwnd, None)
    meu = k32.GetCurrentThreadId()
    u32.AttachThreadInput(meu, alvo, True)
    try:
        est = (ctypes.c_ubyte * 256)(); u32.GetKeyboardState(est)
        antes = bytes(est)
        for m in mods:
            est[VK[m]] |= 0x80
            est[{"ctrl": 0xA2, "shift": 0xA0, "alt": 0xA4}[m]] |= 0x80
        u32.SetKeyboardState(est)
        u32.PostMessageW(hwnd, 0x100, vk, _lp_tecla(vk)); time.sleep(0.05)
        u32.PostMessageW(hwnd, 0x101, vk, _lp_tecla(vk, True))
        time.sleep(0.8)
        volta = (ctypes.c_ubyte * 256)(*antes)
        u32.SetKeyboardState(volta)
    finally:
        u32.AttachThreadInput(meu, alvo, False)


# ---------------------------------------------------------------- janela
def moldura(h):
    r = W.RECT()
    dwm.DwmGetWindowAttribute(W.HWND(h), 9, ctypes.byref(r), ctypes.sizeof(r))
    return r.left, r.top, r.right, r.bottom


def tamanho_kaique(h=None, x=40, y=40):
    """Moldura VISIVEL da janela = 1280 x 657 pontos (logico) x escala deste PC."""
    h = h or principal()
    u32.ShowWindow(h, 4)  # SW_SHOWNOACTIVATE (tira do maximizado)
    alvo_w, alvo_h = round(LOGICO[0] * ESCALA), round(LOGICO[1] * ESCALA)
    for _ in range(3):
        r = W.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
        l, t, rr, b = moldura(h)
        extra_w = (r.right - r.left) - (rr - l)
        extra_h = (r.bottom - r.top) - (b - t)
        u32.SetWindowPos(h, 0, x - (l - r.left), y - (t - r.top), alvo_w + extra_w, alvo_h + extra_h, 0x4 | 0x10)
        time.sleep(0.5)
    l, t, rr, b = moldura(h)
    return rr - l, b - t


def printar(nome, h=None, pasta=BASE):
    import cv2
    import numpy as np
    h = h or principal()
    u32.RedrawWindow(h, None, None, 0x1 | 0x100 | 0x80)
    time.sleep(0.6)
    r = W.RECT(); u32.GetWindowRect(h, ctypes.byref(r))
    w, hh = r.right - r.left, r.bottom - r.top
    hdc = u32.GetWindowDC(h); mem = g32.CreateCompatibleDC(hdc)
    bmp = g32.CreateCompatibleBitmap(hdc, w, hh); g32.SelectObject(mem, bmp)
    u32.PrintWindow(h, mem, 2)

    class BIH(ctypes.Structure):
        _fields_ = [("biSize", W.DWORD), ("biWidth", W.LONG), ("biHeight", W.LONG),
                    ("biPlanes", W.WORD), ("biBitCount", W.WORD), ("biCompression", W.DWORD),
                    ("biSizeImage", W.DWORD), ("biXPelsPerMeter", W.LONG), ("biYPelsPerMeter", W.LONG),
                    ("biClrUsed", W.DWORD), ("biClrImportant", W.DWORD)]
    bi = BIH(); bi.biSize = ctypes.sizeof(BIH); bi.biWidth = w; bi.biHeight = -hh
    bi.biPlanes = 1; bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * hh * 4)
    g32.GetDIBits(mem, bmp, 0, hh, buf, ctypes.byref(bi), 0)
    img = np.frombuffer(buf, np.uint8).reshape(hh, w, 4)[:, :, :3]
    g32.DeleteObject(bmp); g32.DeleteDC(mem); u32.ReleaseDC(h, hdc)
    l, t, rr, b = moldura(h)
    img = img[t - r.top: b - r.top, l - r.left: rr - r.left]
    destino = Path(pasta) / f"{nome}.png"
    cv2.imencode(".png", img)[1].tofile(str(destino))
    return destino, img.shape[1], img.shape[0]


def erros_log():
    f = DADOS / "local" / "EditorImpressao" / "erros.log"
    return f.read_text(encoding="utf-8", errors="replace") if f.exists() else ""
