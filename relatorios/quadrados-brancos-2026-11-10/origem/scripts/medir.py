"""Mede, nas paginas que rodar_versao.py gravou, os buracos brancos na pintura e a tinta de letra
que sumiu. A mesma conta para todas as versoes (as medidas do relatorio do verificador, com o
branco a partir de 250 para valer tambem na copia pequena em JPEG).

    python medir.py <livro.pdf> <saida.json> <pasta:filtro> [<pasta:filtro> ...]

Por pagina e por versao:
  buraco_pintura_pct  dentro da caixa da pintura (achada no ORIGINAL pela cor, como no relatorio
                      do verificador), os pontos que sairam branco puro onde o original NAO era
                      papel (luz abaixo de 90% do papel). Pintura bem tratada: perto de 0.
  blocos              pedacos desse branco do tamanho de meio quadradinho do JPEG ou mais
                      (na escala da imagem medida).
  tinta_sumida_pct    fora da pintura, dos pontos de tinta do original (abaixo de 65% do
                      papel), quantos sairam branco puro (letra quebrada: o "i" e o "t" finos).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np


def original(doc, numero: int, forma) -> np.ndarray:
    pix = doc[numero - 1].get_pixmap(dpi=150 if forma[0] < 2000 else 300)
    o = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3][:, :, ::-1]
    return cv2.resize(np.ascontiguousarray(o), (forma[1], forma[0]), interpolation=cv2.INTER_AREA)


def caixa(bgr: np.ndarray):
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    papel_s = float(np.percentile(hsv[:, :, 1], 30))
    h, w = hsv.shape[:2]
    m = (hsv[:, :, 1].astype(np.float32) > papel_s + 35).astype(np.uint8)
    m[: int(0.04 * h)] = 0; m[-int(0.04 * h):] = 0; m[:, : int(0.04 * w)] = 0; m[:, -int(0.04 * w):] = 0
    k = max(3, int(round(15 * w / 550)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((max(3, k * 9 // 15),) * 2, np.uint8))
    n, _r, st, _c = cv2.connectedComponentsWithStats(m, 8)
    if n <= 1:
        return None
    i = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
    x, y, bw, bh, area = st[i]
    if area < 0.03 * h * w:
        return None
    dx, dy = int(0.03 * bw), int(0.03 * bh)
    return x + dx, y + dy, x + bw - dx, y + bh - dy


def medir(orig: np.ndarray, out: np.ndarray) -> dict:
    g = cv2.cvtColor(orig, cv2.COLOR_BGR2GRAY).astype(np.float32)
    nivel = float(np.percentile(g, 85))
    branco = out.min(axis=2) >= 250
    cx = caixa(orig)
    res = {"tem_pintura": cx is not None}
    fora = np.ones(g.shape, bool)
    if cx is not None:
        x0, y0, x1, y1 = cx
        nao_papel = g[y0:y1, x0:x1] < 0.90 * nivel
        buraco = branco[y0:y1, x0:x1] & nao_papel
        res["buraco_pintura_pct"] = round(100 * float(buraco.mean()), 2)
        meio_quadrado = 0.5 * (24 * out.shape[1] / 2480) ** 2 * 1.0
        n, _r, st, _c = cv2.connectedComponentsWithStats(buraco.astype(np.uint8), 8)
        res["blocos"] = int((st[1:, cv2.CC_STAT_AREA] >= max(4, meio_quadrado)).sum())
        fora[max(0, y0 - 10):y1 + 10, max(0, x0 - 10):x1 + 10] = False
    h, w = g.shape
    borda = np.zeros(g.shape, bool)
    borda[int(0.04 * h):-int(0.04 * h), int(0.04 * w):-int(0.04 * w)] = True
    tinta = (g < 0.65 * nivel) & fora & borda
    res["tinta_sumida_pct"] = round(100 * float((branco & tinta).sum()) / max(1, int(tinta.sum())), 2)
    return res


def main() -> None:
    pdf, destino = sys.argv[1], Path(sys.argv[2])
    doc = fitz.open(pdf)
    res = json.loads(destino.read_text(encoding="utf-8")) if destino.exists() else {}
    for par in sys.argv[3:]:
        pasta, filtro = par.rsplit(":", 1)
        chave = f"{Path(pasta).parent.name}/{Path(pasta).name}:{filtro}"
        res[chave] = {}
        for arq in sorted(Path(pasta).glob(f"{filtro}_p*.jpg")):
            numero = int(arq.stem.rsplit("_p", 1)[1])
            png = arq.with_suffix(".png")
            out = cv2.imread(str(png if png.exists() else arq))
            res[chave][numero] = medir(original(doc, numero, out.shape), out)
        print(chave, {k: v for k, v in list(res[chave].items())[:3]}, flush=True)
    destino.write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
