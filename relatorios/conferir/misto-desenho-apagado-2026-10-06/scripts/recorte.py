"""Recorta o mesmo pedaco de uma pagina nos cinco quadros (Original | Misto de
hoje | Misto consertado | Preto e branco puro | Onde mudou) e grava um jpg,
para olhar de perto e para as figuras do relatorio (06/10/2026).

O quinto quadro e separado (copia clareada do original com o que mudou em azul
transparente): nada e desenhado por cima dos outros quatro.

Uso: python recorte.py pagina x0 y0 x1 y1 [saida.jpg] [largura]
     (x0..y1 em fracao da pagina, 0 a 1; pagina = nome como em trabalho/base)
"""

from __future__ import annotations

import sys

import cv2
import numpy as np

import comum
from comparar import _bgr, _montar, _onde_mudou

T = comum.TRABALHO


def recortar(nome, x0, y0, x1, y1, saida=None, largura=430):
    z = np.load(T / "base" / f"{nome}.npz")
    antes = cv2.imread(str(T / "antes" / f"{nome}.png"), cv2.IMREAD_UNCHANGED)
    depois = cv2.imread(str(T / "depois" / f"{nome}.png"), cv2.IMREAD_UNCHANGED)
    tinta_a = _bgr(antes).min(axis=2) < 128
    tinta_d = _bgr(depois).min(axis=2) < 128
    mudou = tinta_a ^ tinta_d
    a, l = mudou.shape
    ya, yb, xa, xb = int(y0 * a), int(y1 * a), int(x0 * l), int(x1 * l)
    partes = [p[ya:yb, xa:xb] for p in (z["img"], antes, depois, z["pb"], _onde_mudou(z["img"], mudou))]
    saida = saida or str(T / "recortes" / f"{nome}__{x0}_{y0}.jpg")
    (T / "recortes").mkdir(exist_ok=True)
    cv2.imwrite(saida, _montar(partes, largura), [cv2.IMWRITE_JPEG_QUALITY, 90])
    return saida


if __name__ == "__main__":
    args = sys.argv[1:]
    caixa = [float(v) for v in args[1:5]]
    print(recortar(args[0], *caixa, *(args[5:6] or [None]), *([int(args[6])] if len(args) > 6 else [])))
