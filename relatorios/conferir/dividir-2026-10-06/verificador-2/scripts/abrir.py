"""Abre o programa (codigo de VERIF_RAIZ) fora da tela, no tamanho do Kaique."""
import time, ctypes, ctypes.wintypes as W
import piloto as P
def abrir():
    h = P.iniciar(); time.sleep(3)
    P.u32.ShowWindow(h, 4)
    aw, ah = round(P.LOGICO[0]*P.ESCALA), round(P.LOGICO[1]*P.ESCALA)
    for _ in range(3):
        r = W.RECT(); P.u32.GetWindowRect(h, ctypes.byref(r)); l, t, rr, b = P.moldura(h)
        P.u32.SetWindowPos(h, 0, -32000, -32000, aw+(r.right-r.left)-(rr-l), ah+(r.bottom-r.top)-(b-t), 0x4 | 0x10); time.sleep(0.4)
    return h
