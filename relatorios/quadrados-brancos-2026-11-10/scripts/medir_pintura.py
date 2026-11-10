"""Medida 2 (corrige a 1, que nao via o branco nas partes CLARAS da pintura, como o ceu):
dentro da caixa da pintura (achada no original pela cor, como em montar.py), a fracao de pontos
que sairam BRANCO PURO (>= 250 nos tres canais) onde o original NAO era branco de papel
(luz abaixo de 90% do nivel do papel da pagina). Numa pintura bem tratada isso fica perto de 0.
Uso: python medir_pintura.py <livro.pdf> <pasta:variante> [<pasta:variante> ...]"""
import json
import sys

import cv2
import fitz
import numpy as np


def caixa(rgb):
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    papel_s = float(np.percentile(hsv[:, :, 1], 30))
    h, w = hsv.shape[:2]
    m = (hsv[:, :, 1].astype(np.float32) > papel_s + 35).astype(np.uint8)
    m[: int(0.04 * h)] = 0; m[-int(0.04 * h):] = 0; m[:, : int(0.04 * w)] = 0; m[:, -int(0.04 * w):] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    n, _r, st, _c = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, bw, bh, area = st[i]
    if area < 0.03 * h * w:
        return None
    dx, dy = int(0.03 * bw), int(0.03 * bh)
    return x + dx, y + dy, x + bw - dx, y + bh - dy


pdf = sys.argv[1]
doc = fitz.open(pdf)
pares = [a.split(":") for a in sys.argv[2:]]
res = {f"{p}:{v}": {} for p, v in pares}
for n in range(1, len(doc) + 1):
    pix = doc[n - 1].get_pixmap(dpi=75)
    o = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].copy()  # RGB
    cx = caixa(o)
    for pasta, v in pares:
        out = cv2.imread(f"{pasta}/{v}_p{n:03d}.jpg")
        if cx is None or out is None:
            res[f"{pasta}:{v}"][n] = None
            continue
        oo = cv2.resize(o, (out.shape[1], out.shape[0]), interpolation=cv2.INTER_AREA)
        sx, sy = out.shape[1] / o.shape[1], out.shape[0] / o.shape[0]
        x0, y0, x1, y1 = int(cx[0] * sx), int(cx[1] * sy), int(cx[2] * sx), int(cx[3] * sy)
        g = cv2.cvtColor(oo, cv2.COLOR_RGB2GRAY).astype(np.float32)
        nivel = float(np.percentile(g, 85))
        nao_branco = g[y0:y1, x0:x1] < 0.90 * nivel
        branco = out[y0:y1, x0:x1].min(axis=2) >= 250
        res[f"{pasta}:{v}"][n] = round(100 * float((branco & nao_branco).mean()), 2)
json.dump(res, open("medida_pintura.json", "w"), indent=1)
for k, d in res.items():
    vals = {n: x for n, x in d.items() if x is not None}
    def conta(lim):
        return sum(1 for x in vals.values() if x >= lim)
    print(k, "paginas com pintura:", len(vals), "| >=2%:", conta(2), "| >=0,5%:", conta(0.5),
          "| media %.2f" % (sum(vals.values()) / max(1, len(vals))),
          "| piores:", sorted(vals.items(), key=lambda a: -a[1])[:6])
