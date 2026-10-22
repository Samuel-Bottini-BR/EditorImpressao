"""Verificador 22/10: a conta "so o preto" de antes (c66f28d) e a de depois (49d1ed3) em paginas de verdade a
300 DPI (folha inteira, cor e cinza): mesmo resultado? quanto tempo cada uma?"""
import importlib.util, sys, time
import fitz, numpy as np
W = "D:/programas/EditorImpressao/.claude/worktrees"
def carregar(lado):
    s = importlib.util.spec_from_file_location("bp_" + lado, f"{W}/vcx22-{lado}/core/borda_preta.py")
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m); return m
A, B = carregar("antes"), carregar("novo")
import cv2
dif = n = 0; ta = tb = 0.0
for pdf, quais in ((sys.argv[1], range(14)), (sys.argv[2], range(0, 100, 4))):
    d = fitz.open(pdf)
    for i in quais:
        pm = d[i].get_pixmap(dpi=300)
        img = np.frombuffer(pm.samples, np.uint8).reshape(pm.height, pm.width, pm.n)[:, :, :3][:, :, ::-1].copy()
        for x in (img, cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)):
            t = time.perf_counter(); ra = A.so_o_preto(x); ta += time.perf_counter() - t
            t = time.perf_counter(); rb = B.so_o_preto(x); tb += time.perf_counter() - t
            n += 1; dif += ra != rb
            if ra != rb: print("DIFERENTE", pdf[-20:], i, ra, rb)
print(f"contas {n}, diferentes {dif}, antes {ta:.1f} s, depois {tb:.1f} s, {ta/tb:.1f} vezes")
