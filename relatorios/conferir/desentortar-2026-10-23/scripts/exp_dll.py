import sys, cv2, numpy as np
sys.path.insert(0, r"D:\programas\EditorImpressao\.claude\worktrees\v212")
from core import desentortar_scantailor as ds
img = cv2.imread(sys.argv[1])
for dpi in (300, 200, 400):
  for lado in (0, 1, 2):
    for cont in (None, "caixa"):
        c = None
        if cont:
            x0,y0,x1,y1 = ds.caixa_do_conteudo(img, (0,0,img.shape[1],img.shape[0]), dpi); c=(x0,y0,x1-x0,y1-y0)
        r = ds.desentortar(img, dpi, ds.AUTOMATICO, lado=lado, conteudo=c)
        if r.imagem is None: print(dpi,lado,cont,"falhou",r.motivo); continue
        d = cv2.absdiff(r.imagem, img).max(axis=2)
        print(dpi, lado, cont, "achou", r.achou_curvas, "mudou>32:", int((d>32).sum()))
