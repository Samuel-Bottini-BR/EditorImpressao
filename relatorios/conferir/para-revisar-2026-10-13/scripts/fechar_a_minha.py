"""Fecha (WM_CLOSE) uma janela de teste MINHA que ficou aberta, pelo pid do lancador (so processos do meu lancador2.py)."""
import sys, time, ctypes, ctypes.wintypes as W, psutil
u32 = ctypes.WinDLL("user32")
pids = set()
for arg in sys.argv[1:]:
    p = psutil.Process(int(arg))
    assert "lancador2.py" in " ".join(p.cmdline()), "nao e o meu lancador"
    pids |= {p.pid} | {c.pid for c in p.children(recursive=True)}
achadas = []
@ctypes.WINFUNCTYPE(W.BOOL, W.HWND, W.LPARAM)
def cada(h, _):
    pid = W.DWORD(); u32.GetWindowThreadProcessId(h, ctypes.byref(pid))
    if pid.value in pids and u32.IsWindowVisible(h):
        t = ctypes.create_unicode_buffer(200); u32.GetWindowTextW(h, t, 200); achadas.append((h, t.value))
    return True
u32.EnumWindows(cada, 0)
print("janelas:", achadas)
for h, t in achadas:
    u32.PostMessageW(W.HWND(h), 0x10, 0, 0)
time.sleep(12)
print("ainda vivos:", [p for p in pids if psutil.pid_exists(p)])
