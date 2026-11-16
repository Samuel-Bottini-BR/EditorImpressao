"""Ajudante para pilotar o programa EMPACOTADO (o .exe) sem aparecer na tela do Samuel.

Roda DENTRO de uma área de trabalho escondida do Windows (ver lancar.py: CreateDesktop + CreateProcess com
lpDesktop). Ali a janela existe de verdade (com fonte), mas nunca aparece na tela dele. Os botões são
apertados pelo UI Automation do Windows ("Invoke", o que um leitor de tela faz), sem mouse nem teclado;
os prints saem por PrintWindow. Usa o Python 3.12 do sistema (pywinauto 0.6.9 + pywin32), que não importa
nada do programa: o programa é só o .exe.
"""
from __future__ import annotations

import json
import os
import subprocess
import time
from ctypes import windll
from pathlib import Path

import win32gui
import win32ui
from PIL import Image
from pywinauto import Desktop

LOG = None


def abrir_log(caminho: Path):
    global LOG
    caminho.parent.mkdir(parents=True, exist_ok=True)
    LOG = open(caminho, "a", encoding="utf-8")


def anotar(chave, valor=None):
    linha = f"{time.strftime('%H:%M:%S')} {chave} => {json.dumps(valor, ensure_ascii=False, default=str)}"
    print(linha, flush=True)
    if LOG:
        LOG.write(linha + "\n"); LOG.flush()


def lancar_exe(exe: Path, dados: Path, temp: Path, argumentos=()) -> subprocess.Popen:
    """Abre o .exe com a pasta de dados e o TEMP trocados (nunca a pasta de dados do Samuel)."""
    amb = dict(os.environ)
    amb["LOCALAPPDATA"] = str(dados)
    amb["TEMP"] = amb["TMP"] = str(temp)
    amb.pop("QT_QPA_PLATFORM", None)
    dados.mkdir(parents=True, exist_ok=True)
    temp.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen([str(exe), *map(str, argumentos)], env=amb, cwd=str(exe.parent))


def janela_principal(pid: int, limite=120):
    d = Desktop(backend="uia")
    fim = time.time() + limite
    while time.time() < fim:
        for w in d.windows():
            try:
                if w.process_id() == pid and "Editor de Impress" in w.window_text():
                    return w
            except Exception:
                pass
        time.sleep(0.5)
    raise RuntimeError("a janela do programa não apareceu")


def janelas_do_processo(pid: int):
    """As janelas do programa: as de cima e as que abriram por cima delas. No leitor de tela do Windows,
    uma janela de diálogo com dona (QDialog com pai) aparece DENTRO da dona, não ao lado."""
    out = []
    for w in Desktop(backend="uia").windows():
        try:
            if w.process_id() == pid:
                out.append(w)
                for d in w.descendants(control_type="Window"):
                    if d.element_info.handle:
                        out.append(d)
        except Exception:
            pass
    return out


def descrever(w, destino: Path):
    """Lista o que o leitor de tela vê na janela (nome, tipo, se está ligado), para achar os botões."""
    linhas = []
    for e in w.descendants():
        try:
            ei = e.element_info
            linhas.append(f"{ei.control_type}\t{ei.name!r}\t{ei.automation_id}\t"
                          f"vis={e.is_visible()}\tlig={e.is_enabled()}\t{e.rectangle()}")
        except Exception as erro:
            linhas.append(f"? {erro}")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("\n".join(linhas), encoding="utf-8")
    return linhas


def achar(w, nome: str, tipo: str | None = None, contem=False, visivel=True, limite=30):
    fim = time.time() + limite
    while time.time() < fim:
        for e in w.descendants(control_type=tipo) if tipo else w.descendants():
            try:
                n = e.element_info.name or ""
                if (nome in n if contem else n == nome) and (not visivel or e.is_visible()):
                    return e
            except Exception:
                pass
        time.sleep(0.5)
    raise RuntimeError(f"não achei {tipo or ''} {nome!r}")


def apertar(w, nome: str, tipo: str | None = "Button", contem=False, limite=30):
    e = achar(w, nome, tipo, contem=contem, limite=limite)
    try:
        e.invoke()
    except Exception:
        e.iface_legacy_iaccessible.DoDefaultAction()
    anotar("apertei", nome)
    time.sleep(0.8)
    return e


def print_janela(w, destino: Path):
    """Print da janela por PrintWindow (PW_RENDERFULLCONTENT)."""
    h = w.handle
    l, t, r, b = win32gui.GetWindowRect(h)
    W, H = r - l, b - t
    hdc = win32gui.GetWindowDC(h)
    mfc = win32ui.CreateDCFromHandle(hdc)
    sdc = mfc.CreateCompatibleDC()
    bmp = win32ui.CreateBitmap()
    bmp.CreateCompatibleBitmap(mfc, W, H)
    sdc.SelectObject(bmp)
    windll.user32.PrintWindow(h, sdc.GetSafeHdc(), 2)
    info = bmp.GetInfo()
    img = Image.frombuffer("RGB", (info["bmWidth"], info["bmHeight"]), bmp.GetBitmapBits(True),
                           "raw", "BGRX", 0, 1)
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino)
    win32gui.DeleteObject(bmp.GetHandle()); sdc.DeleteDC(); mfc.DeleteDC(); win32gui.ReleaseDC(h, hdc)
    anotar("print", destino.name)
    return destino


def fechar(w):
    WM_CLOSE = 0x0010
    win32gui.PostMessage(w.handle, WM_CLOSE, 0, 0)


def clicar(w, elemento, duplo=False):
    """Clique esquerdo por mensagens do Windows (PostMessage ao hwnd da janela), no meio do elemento.
    Não usa o mouse do Samuel; a janela está na área escondida."""
    import win32api
    import win32con
    r = elemento.rectangle()
    cx, cy = (r.left + r.right) // 2, (r.top + r.bottom) // 2
    x, y = win32gui.ScreenToClient(w.handle, (cx, cy))
    lp = win32api.MAKELONG(x & 0xFFFF, y & 0xFFFF)
    h = w.handle
    win32gui.PostMessage(h, win32con.WM_MOUSEMOVE, 0, lp); time.sleep(0.15)
    win32gui.PostMessage(h, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lp); time.sleep(0.1)
    win32gui.PostMessage(h, win32con.WM_LBUTTONUP, 0, lp); time.sleep(0.4)
    if duplo:
        win32gui.PostMessage(h, win32con.WM_LBUTTONDBLCLK, win32con.MK_LBUTTON, lp); time.sleep(0.1)
        win32gui.PostMessage(h, win32con.WM_LBUTTONUP, 0, lp); time.sleep(0.4)
    anotar("cliquei", f"{elemento.element_info.name!r} em {x},{y}")


def esperar_janela(pid: int, titulo_contem: str, limite=60):
    fim = time.time() + limite
    while time.time() < fim:
        for x in janelas_do_processo(pid):
            if titulo_contem in (x.window_text() or ""):
                return x
        time.sleep(0.5)
    return None


def descrever_tudo(pid: int, pasta: Path, nome: str):
    """Print e lista de cada janela do programa (a principal e as que abriram por cima)."""
    for k, x in enumerate(janelas_do_processo(pid)):
        try:
            print_janela(x, pasta / f"{nome}-{k}.png")
            descrever(x, pasta / f"{nome}-{k}.txt")
            anotar("janela", [k, x.window_text()])
        except Exception as erro:
            anotar("erro ao descrever", str(erro))
