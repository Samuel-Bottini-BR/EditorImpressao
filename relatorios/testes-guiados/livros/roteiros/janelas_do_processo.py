"""De fora: lista as janelas visíveis de um processo (o meu, pelo PID) e tira o print de cada uma
com PrintWindow, sem mexer nelas. Para ver uma caixa que travou o roteiro.
Uso: python janelas_do_processo.py <pid> <pasta>"""
import ctypes
import ctypes.wintypes as wt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from base import BITMAPINFOHEADER  # noqa: E402
from PIL import Image  # noqa: E402

user32, gdi32 = ctypes.windll.user32, ctypes.windll.gdi32
pid_alvo, pasta = int(sys.argv[1]), Path(sys.argv[2])
pasta.mkdir(parents=True, exist_ok=True)
achadas = []


@ctypes.WINFUNCTYPE(wt.BOOL, wt.HWND, wt.LPARAM)
def cada(h, _):
    pid = wt.DWORD()
    user32.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value == pid_alvo and user32.IsWindowVisible(h):
        t = ctypes.create_unicode_buffer(300)
        user32.GetWindowTextW(h, t, 300)
        r = wt.RECT(); user32.GetWindowRect(h, ctypes.byref(r))
        achadas.append((h, t.value, (r.left, r.top, r.right - r.left, r.bottom - r.top)))
    return True


user32.EnumWindows(cada, 0)
for k, (h, titulo, ret) in enumerate(achadas):
    print(k, hex(h), repr(titulo), ret)
    w, a = ret[2], ret[3]
    if w <= 0 or a <= 0:
        continue
    dc = user32.GetWindowDC(h); mdc = gdi32.CreateCompatibleDC(dc)
    bmp = gdi32.CreateCompatibleBitmap(dc, w, a); gdi32.SelectObject(mdc, bmp)
    user32.PrintWindow(h, mdc, 2)
    bi = BITMAPINFOHEADER(); bi.biSize = ctypes.sizeof(bi); bi.biWidth = w; bi.biHeight = -a
    bi.biPlanes = 1; bi.biBitCount = 32
    buf = ctypes.create_string_buffer(w * a * 4)
    gdi32.GetDIBits(mdc, bmp, 0, a, buf, ctypes.byref(bi), 0)
    gdi32.DeleteObject(bmp); gdi32.DeleteDC(mdc); user32.ReleaseDC(h, dc)
    Image.frombuffer("RGBA", (w, a), buf, "raw", "BGRA", 0, 1).convert("RGB").save(pasta / f"janela-{k}.png")
