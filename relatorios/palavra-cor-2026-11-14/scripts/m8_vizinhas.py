"""Medida 8 (estudo D-701, para o print das opções): acha, na Horas 26, duas palavras VIZINHAS (na
mesma linha, uma logo depois da outra) que saem com cores diferentes na opção 2 (cada palavra numa
cor, com as caixas do ScanTailor) e com a mesma cor na opção 1 (a mesma tinta, a mesma cor).

Lê _dados/m4 (a tinta) e _dados/m5-v3 (as simulações). Cor da palavra = a cor que mais aparece na
tinta dela. Imprime os pares com a maior diferença na opção 2 (LAB) e a diferença na opção 1, para a
tela (110) e o PDF (300). Não muda nada do programa.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
DADOS = AQUI.parent / "_dados"


def lab(bgr):
    v = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2LAB)[0, 0].astype(float)
    return np.array([v[0] * 100 / 255, v[1] - 128, v[2] - 128])


def pares(dpi):
    tinta = cv2.imread(str(DADOS / "m4" / f"horas_p026_{dpi}_pb.png"), 0) == 0
    a = cv2.imread(str(DADOS / "m5-v3" / f"horas_p026_{dpi}_A.png"))
    b = cv2.imread(str(DADOS / "m5-v3" / f"horas_p026_{dpi}_B.png"))
    H, W = tinta.shape
    y0, y1, x0, x1 = int(0.149 * H), int(0.788 * H), int(0.037 * W), int(0.915 * W)
    t8 = tinta.astype(np.uint8)
    _, _, cx, _ = cv2.connectedComponentsWithStats(t8, connectivity=8)
    h = float(np.median(cx[1:, 3][cx[1:, 4] > 20]))
    junto = cv2.morphologyEx(t8, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (max(3, int(0.35 * h)), 1)))
    n, rot, caixas, _ = cv2.connectedComponentsWithStats(junto, connectivity=8)
    palavras = []
    for r in range(1, n):
        x, y, w, hh, area = caixas[r]
        if not (y0 <= y and y + hh <= y1 and x0 <= x and x + w <= x1) or hh < 0.6 * h or w < 1.5 * h:
            continue
        pts = (rot == r) & tinta
        ca = Counter(map(tuple, a[pts].tolist())).most_common(1)[0][0]
        cb = Counter(map(tuple, b[pts].tolist())).most_common(1)[0][0]
        palavras.append((x, y, w, hh, ca, cb))
    saida = []
    for p in palavras:
        for q in palavras:
            meio_p, meio_q = p[1] + p[3] / 2, q[1] + q[3] / 2
            if q[0] <= p[0] or abs(meio_p - meio_q) > 0.5 * h or q[0] - (p[0] + p[2]) > 2.5 * h:
                continue
            # q é a vizinha à direita de p (a mais próxima)
            da = float(np.linalg.norm(lab(p[4]) - lab(q[4])))
            db = float(np.linalg.norm(lab(p[5]) - lab(q[5])))
            saida.append((da, db, p[:4], q[:4], p[4], q[4], p[5], q[5]))
    saida.sort(key=lambda s: -(s[0] - 3 * s[1]))
    return saida


if __name__ == "__main__":
    for dpi in (int(a) for a in (sys.argv[1:] or ["300", "110"])):
        print("== dpi", dpi)
        for s in pares(dpi)[:12]:
            print(f"op2 dif={s[0]:5.1f} op1 dif={s[1]:4.1f}  p={s[2]} q={s[3]}  op2 {s[4]}/{s[5]}  op1 {s[6]}/{s[7]}")
