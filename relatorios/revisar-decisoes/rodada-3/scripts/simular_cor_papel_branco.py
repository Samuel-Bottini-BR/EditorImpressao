"""SIMULACAO (nao e o programa de hoje): como ficaria a letra S do Graduale
588 com uma zona do tipo "Tinta com a cor original, papel branco" (P11 da
conferencia 12, decidida e ainda nao feita).

Usa a conta que o programa JA tem para a decoracao colorida (moldura dourada,
iluminura) no Misto: core.filtros._com_a_decoracao (a tinta fica com a cor,
o papel ligado ao de fora vai a branco), aplicada so dentro de um retangulo
desenhado a mao em volta da letra, por cima do resultado de fabrica.
Entradas: as imagens a 4000 px que o rodar.py gravou (original e jeito A).

Uso: python simular_cor_papel_branco.py  (grava <TRABALHO>/marcar/graduale588-S-cor-papel-branco.jpg)
"""
import sys

import cv2
import numpy as np

import comum

sys.path.insert(0, str(comum.RAIZ))
from core import filtros as F  # noqa: E402

BASE = "graduale_p588__inteira"
RET = (0.07, 0.285, 0.34, 0.475)


def main() -> None:
    ori = cv2.imread(str(comum.DADOS / f"{BASE}__original.jpg"))
    a = cv2.imread(str(comum.DADOS / f"{BASE}__a.jpg"))
    a = cv2.resize(a, (ori.shape[1], ori.shape[0]))
    h, w = ori.shape[:2]
    peso = np.zeros((h, w), np.float32)
    x0, y0, x1, y1 = RET
    peso[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1.0
    ref = F._referencia_do_papel(ori, np.zeros((h, w), bool))
    # a mesma conta de F._com_a_decoracao, mas com uma folga em volta do
    # retangulo: e o papel de FORA (a folga) que diz qual papel vai a branco
    # (sem folga, a caixa e o proprio retangulo e nao sobra "papel de fora")
    m = int(0.03 * min(h, w))
    ya, yb = max(0, int(y0 * h) - m), min(h, int(y1 * h) + m)
    xa, xb = max(0, int(x0 * w) - m), min(w, int(x1 * w) + m)
    fora = peso[ya:yb, xa:xb] <= 0
    tratada = a.copy()
    tratada[ya:yb, xa:xb] = F._decoracao_com_a_cor_original(
        np.ascontiguousarray(ori[ya:yb, xa:xb]), ref, fora=fora,
        area_grande=max(1, int(F.DECORACAO_PAPEL_GRANDE * h * w)),
        letra_max=max(1, int(F.LETRA_NA_DECORACAO_MAX * min(h, w))),
        letras_pretas=False, altura_da_pagina=h,
        lado_largo=max(5, int(min(h, w) * F.DESENHO_FECHAMENTO) | 1))
    saida = F._misturar(a.copy(), tratada, peso)
    destino = comum.TRABALHO / "marcar" / "graduale588-S-cor-papel-branco.jpg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(destino), saida, [cv2.IMWRITE_JPEG_QUALITY, 94])
    print(destino, saida.shape)


if __name__ == "__main__":
    main()
