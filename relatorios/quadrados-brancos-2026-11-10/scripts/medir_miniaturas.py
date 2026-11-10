"""Medida mais firme sobre as miniaturas (75 DPI) gravadas por varrer.py: o original desenhado
a 75 DPI x a saida reduzida. Conta os pontos que ficaram BRANCOS onde o original era pintura
de tom medio (entre 45% e 75% da luz do papel), depois de uma abertura 3x3 (tira a franja
fina das letras e o ruido do JPEG da miniatura): sobram so as manchas brancas largas.
Uso: python medir_miniaturas.py <livro.pdf> <pasta> <variante> [paginas]"""
import json
import sys

import cv2
import fitz
import numpy as np

pdf, pasta, variante = sys.argv[1], sys.argv[2], sys.argv[3]
doc = fitz.open(pdf)
res = {}
paginas = [int(v) for v in sys.argv[4].split(",")] if len(sys.argv) > 4 else range(1, len(doc) + 1)
for n in paginas:
    out = cv2.imread(f"{pasta}/{variante}_p{n:03d}.jpg")
    pix = doc[n - 1].get_pixmap(dpi=75)
    o = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3][:, :, ::-1]
    o = cv2.resize(np.ascontiguousarray(o), (out.shape[1], out.shape[0]), interpolation=cv2.INTER_AREA)
    g = cv2.cvtColor(o, cv2.COLOR_BGR2GRAY).astype(np.float32)
    nivel = float(np.percentile(g, 85))
    tom_medio = (g < 0.75 * nivel) & (g > 0.45 * nivel)
    branco = out.min(axis=2) >= 245
    novo = (branco & tom_medio).astype(np.uint8)
    novo = cv2.morphologyEx(novo, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    mh, mw = int(0.06 * novo.shape[0]), int(0.06 * novo.shape[1])   # fora a beirada do scan
    novo[:mh] = 0; novo[-mh:] = 0; novo[:, :mw] = 0; novo[:, -mw:] = 0
    res[n] = {"manchas_brancas_pct": round(100 * float(novo.mean()), 3),
              "tom_medio_pct": round(100 * float(tom_medio.mean()), 1)}
json.dump(res, open(f"{pasta}/{variante}_mini.json", "w"), indent=1)
b = sorted(((v["manchas_brancas_pct"], k) for k, v in res.items()), reverse=True)
print(" ".join(f"{k}:{v}" for v, k in b))
