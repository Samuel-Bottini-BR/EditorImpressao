"""Righetti 96 direita: o desentortar com a imagem inteira x com uma caixa que deixa a faixa preta de fora."""
import sys
sys.path.insert(0, "D:/programas/EditorImpressao/.claude/worktrees/fase2-itens")
import cv2, numpy as np
from core import pipeline, desentortar_scantailor as ds
from core.filtros import ORIGINAL
from core.pdf_io import abrir_pdf
from modelos import Projeto
pdf = "D:/programas/EditorImpressao/.claude/worktrees/fase2-itens/saida_teste/2.12/righettig_91a110.pdf"
p = pipeline.analisar_projeto(Projeto(caminho_entrada=pdf, nome="r", dividir_folhas=True))
pg = [x for x in p.paginas if x.folha == 5 and x.metade == "direita"][0]
pg.filtro = ORIGINAL
doc = abrir_pdf(pdf)
img, _ = pipeline.renderizar_pagina(doc, p, pg, dpi=p.qualidade_dpi)
cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
h, w = cinza.shape
linhas_pretas = np.where((cinza < 60).mean(axis=1) > 0.6)[0]
faixa = int(linhas_pretas.max()) + 1 if len(linhas_pretas) and linhas_pretas.min() < h * 0.1 else 0
tinta = np.where((cinza[faixa + 20:] < 128).mean(axis=1) > 0.01)[0]
y0 = faixa + 20 + int(tinta.min()); y1 = faixa + 20 + int(tinta.max())
colunas = np.where((cinza[y0:y1] < 128).mean(axis=0) > 0.01)[0]
x0, x1 = int(colunas.min()), int(colunas.max())
print("imagem", (w, h), "faixa preta ate y", faixa, "caixa", (x0, y0, x1 - x0, y1 - y0))
saidas = {}
for nome, LADO in (("inteira", 2), ("caixa", 0)):
    r = ds.desentortar(img, p.qualidade_dpi, ds.AUTOMATICO, lado=LADO, conteudo=None)
    o = r.imagem
    oc = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY) if o.ndim == 3 else o
    col = np.where((oc[faixa + 50:] < 128).mean(axis=0) > 0.01)[0]
    print(nome, "curvas", r.achou_curvas, "tinta de x", int(col.min()), "a", int(col.max()), "(antes", x0, "a", x1, ")")
    saidas[nome] = o
alt = 900
fx = alt / h
lado = [cv2.resize(x, None, fx=fx, fy=fx) for x in (img, saidas["inteira"], saidas["caixa"])]
cv2.imwrite("D:/programas/EditorImpressao/.claude/worktrees/fase2-itens/saida_teste/2.12/hipotese_lado.jpg",
            np.hstack([np.dstack([x] * 3) if x.ndim == 2 else x for x in lado]))
