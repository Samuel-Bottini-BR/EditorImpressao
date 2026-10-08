"""Rodada 4, o "delineado": nas 89 paginas, quantas areas o programa acha como
gravura e quantas a conta de "suspeita" (figuras4.f_gravura) pinta de laranja:
contraste dentro da area < 60 niveis de cinza (so mancha) ou tiras finas na
beirada (encosta na beirada e ocupa menos de 30% da propria caixa).
Uso: python zonas_teste.py   (grava <TRABALHO>/zonas-teste.json)"""
import json

import cv2
import numpy as np

import comum
from regra4 import bases_89
from sinais4 import pasta_de


def main() -> None:
    res = {}
    for b in bases_89():
        z = np.load(pasta_de(b) / f"{b}.npz")
        m, cinza = z["imagem"], z["cinza"]
        a, l = m.shape
        n, rot, st, _c = cv2.connectedComponentsWithStats(m.astype(np.uint8), connectivity=8)
        zonas = []
        beir = int(0.01 * min(a, l))
        for i in range(1, n):
            if st[i, cv2.CC_STAT_AREA] < 0.004 * a * l:
                continue
            x, y, w, h = st[i, :4]
            g = cinza[rot == i]
            contraste = float(np.percentile(g, 95) - np.percentile(g, 5))
            toca = x <= beir or y <= beir or x + w >= l - beir or y + h >= a - beir
            cheia = st[i, cv2.CC_STAT_AREA] / max(1, w * h)
            zonas.append({"fracao": round(st[i, cv2.CC_STAT_AREA] / (a * l), 3), "contraste": round(contraste),
                          "suspeita": bool(contraste < 60 or (toca and cheia < 0.3))})
        res[b] = zonas
    com = [b for b, zs in res.items() if zs]
    susp = [b for b, zs in res.items() if any(zz["suspeita"] for zz in zs)]
    print("paginas com gravura achada", len(com), "de", len(res), "; areas", sum(len(z) for z in res.values()))
    print("paginas com area suspeita", len(susp), susp)
    (comum.TRABALHO / "zonas-teste.json").write_text(json.dumps(res, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
