"""Folhas de contato: TODAS as paginas em que as duas ordens dao imagem
diferente, em pares (ordem antiga | ordem nova), 4 pares por folha, para
olhar tambem as que a conta deu como "igual" ou "melhorou" (numero nao da
veredito sozinho). Fundo magenta em volta de cada pagina, para a beirada
branca ou preta aparecer.

USO   python folhas_de_contato.py      ->  img/contato-NN.jpg
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

PASTA = Path(__file__).resolve().parent.parent
FINAIS = PASTA.parents[2] / "_tmp" / "finais"
ALTURA, CELULA = 900, 640
FUNDO = (200, 60, 200)


def _mini(caminho: Path, fator: float) -> np.ndarray:
    img = cv2.imread(str(caminho))
    return cv2.resize(img, (max(1, round(img.shape[1] * fator)), max(1, round(img.shape[0] * fator))),
                      interpolation=cv2.INTER_AREA)


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    classes = json.loads((PASTA / "classificacao.json").read_text(encoding="utf-8"))
    bases = [b for b in sorted(dados) if "C" in dados[b] and not classes[b]["so_a_ordem"]["identica"]]
    (PASTA / "img").mkdir(exist_ok=True)
    for n in range(0, len(bases), 4):
        quadros = []
        for base in bases[n:n + 4]:
            d = dados[base]
            maior = max(d[c]["tamanho_px"][1] for c in "BC")
            maior_l = max(d[c]["tamanho_px"][0] for c in "BC")
            fator = min(ALTURA / maior, (CELULA - 16) / maior_l)
            par = np.full((ALTURA + 60, 2 * CELULA, 3), FUNDO, np.uint8)
            c = classes[base]["so_a_ordem"]
            cv2.putText(par, f"{base.replace('__inteira', '')}  [{c['classe']}]  faixa {c['d_faixa_pp']:+.1f}pp  "
                             f"tinta fora {c['d_tinta_perdida_pp']:+.2f}pp  pecas {c['d_pecas']:+d}  area {c['d_area_pct']:+.1f}%",
                        (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(par, "antiga (B)", (8, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(par, "nova (C)", (CELULA + 8, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            for i, cfg in enumerate("BC"):
                m = _mini(FINAIS / f"{base}__{cfg}.jpg", fator)
                x = i * CELULA + (CELULA - m.shape[1]) // 2
                par[56:56 + m.shape[0], x:x + m.shape[1]] = m
            quadros.append(par)
        while len(quadros) < 4:
            quadros.append(np.full_like(quadros[0], FUNDO))
        folha = np.vstack([np.hstack(quadros[:2]), np.hstack(quadros[2:])])
        destino = PASTA / "img" / f"contato-{n // 4 + 1:02d}.jpg"
        cv2.imwrite(str(destino), folha, [cv2.IMWRITE_JPEG_QUALITY, 80])
        print(destino.name, bases[n:n + 4])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
