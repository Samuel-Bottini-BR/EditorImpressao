import sys, cv2, numpy as np
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\v212")
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\v212\relatorios\conferir\desentortar-2026-10-23\scripts")
from core import desentortar_scantailor as ds
import v212
img = cv2.imread(sys.argv[1]); dpi=300
H,W=img.shape[:2]
x0,y0,x1,y1 = ds.caixa_do_conteudo(img, (0,0,W,H), dpi); print("caixa do conteudo", (x0,y0,x1,y1), "imagem", W, H)
# caixa de tinta feita por mim: só o bloco de texto (sem a moldura escura do scanner)
m = v212.tinta(img)
saidas=[("original", img)]
for nome, c in (("conteudo=imagem inteira", None), ("conteudo=caixa do programa", (x0,y0,x1-x0,y1-y0)), ("conteudo=bloco do texto (eu)", tuple(int(v) for v in sys.argv[2].split(",")))):
    r = ds.desentortar(img, dpi, ds.AUTOMATICO, conteudo=c)
    print(nome, "achou", r.achou_curvas, v212.medidas(r.imagem))
    saidas.append((nome, r.imagem))
print("original", v212.medidas(img))
cv2.imwrite("exp2.jpg", v212.painel(["curvada2 direto na DLL"], [(n, "", i) for n,i in saidas], 1000))
