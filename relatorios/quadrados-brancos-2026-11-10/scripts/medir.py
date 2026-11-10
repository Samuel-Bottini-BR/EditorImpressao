"""Mede os quadrados brancos dentro da gravura: quantos pontos viraram branco puro
(255,255,255) onde o original nao era branco, quantos blocos, e se as bordas caem na
grade do JPEG (16 pontos de cor no arquivo = 24 no PDF a 300 DPI, 12 na previa a 150).
Uso: python medir.py <pasta> <caixa x0,y0,x1,y1 em fracao> <nome...>"""
import sys
from pathlib import Path

import cv2
import numpy as np


def medir(orig, img, caixa, grade):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = (int(round(caixa[0] * w)), int(round(caixa[1] * h)),
                      int(round(caixa[2] * w)), int(round(caixa[3] * h)))
    o = orig[y0:y1, x0:x1]
    s = img[y0:y1, x0:x1]
    branco = (s >= 255).all(axis=2)
    nao_era = o.min(axis=2) < 235
    novo = branco & nao_era
    n, rot, st, _ = cv2.connectedComponentsWithStats(novo.astype(np.uint8), 8)
    grandes = int((st[1:, cv2.CC_STAT_AREA] >= (grade * grade) // 2).sum())
    # bordas verticais do branco (troca branco<->nao branco ao andar na linha)
    dx = np.diff(branco.astype(np.int8), axis=1) != 0
    cols = (np.nonzero(dx)[1] + 1 + x0)
    dy = np.diff(branco.astype(np.int8), axis=0) != 0
    lins = (np.nonzero(dy)[0] + 1 + y0)
    def na_grade(v):
        if v.size == 0:
            return 0.0
        r = v % grade
        return float(((r <= 1) | (r >= grade - 1)).mean())
    return {"branco_novo_pct": round(100 * float(novo.mean()), 2),
            "blocos_grandes": grandes,
            "bordas_na_grade_pct": round(100 * (na_grade(cols) + na_grade(lins)) / 2, 1),
            "esperado_ao_acaso_pct": round(100 * 3 / grade, 1)}


if __name__ == "__main__":
    pasta = Path(sys.argv[1])
    caixa = [float(v) for v in sys.argv[2].split(",")]
    orig_pasta = Path(sys.argv[3])
    for nome in sys.argv[4:]:
        for tipo, grade in (("previa", 12), ("pdf", 24)):
            orig = cv2.imread(str(orig_pasta / f"original_{tipo}.png"))
            img = cv2.imread(str(pasta / f"{nome}_{tipo}.png"))
            print(nome, tipo, medir(orig, img, caixa, grade))
