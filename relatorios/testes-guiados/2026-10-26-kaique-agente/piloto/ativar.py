import sys
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\teste-kaique\relatorios\testes-guiados\2026-10-26-kaique-agente\piloto")
import piloto as P
P.PID = int(open(r"kaique-trabalho\pid.txt").read())
h = P.principal()["hwnd"]
P.user32.PostMessageW(h, 0x0006, 1, 0)   # WM_ACTIVATE
P.user32.PostMessageW(h, 0x0007, 0, 0)   # WM_SETFOCUS
print("ok", h)
