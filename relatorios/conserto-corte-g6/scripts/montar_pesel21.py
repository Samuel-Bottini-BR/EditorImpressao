"""Acerto do Pesel 21 (implementador, 20/10/2026): para cada pagina que muda
(contra o fase-1 ou contra o d97b937; comparacao-pesel21.json), as tres
paginas prontas do livro novo lado a lado, na MESMA escala:
  fase-1 (sem o conserto da cunha) | d97b937 (conserto de 13/10) | agora.
Le as paginas prontas de _tmp/finais ("<base>__C.jpg", "<base>__C__depois.jpg",
"<base>__C__pesel21.jpg", gravadas pelo medir.py). Para o Pesel 21, tambem o
pe da pagina de perto (a legenda que ficava colada na borda).

Grava em relatorios/conferir/conserto-corte-g6-pesel21-2026-10-20/img/ (o
git ignora as imagens; refazem-se com este script). So le; nada muda.

USO  python montar_pesel21.py
"""

from __future__ import annotations

import json
from pathlib import Path

import cv2
import numpy as np

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
FINAIS = RAIZ / "_tmp" / "finais"
DESTINO = RAIZ / "relatorios" / "conferir" / "conserto-corte-g6-pesel21-2026-10-20" / "img"
ALTURA = 1200


def _quadro(img, f, titulo, linha2):
    p = cv2.resize(img, (max(1, round(img.shape[1] * f)), max(1, round(img.shape[0] * f))),
                   interpolation=cv2.INTER_AREA)
    p = cv2.copyMakeBorder(p, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(0, 0, 200))
    altura = max(ALTURA, p.shape[0])
    tela = np.full((altura + 70, p.shape[1] + 24, 3), 228, np.uint8)
    tela[60:60 + p.shape[0], 12:12 + p.shape[1]] = p
    cv2.putText(tela, titulo, (12, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.62, (0, 0, 0), 2, cv2.LINE_AA)
    cv2.putText(tela, linha2, (12, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (40, 40, 40), 1, cv2.LINE_AA)
    return tela


def _lado_a_lado(quadros):
    altura = max(q.shape[0] for q in quadros)
    return np.hstack([cv2.copyMakeBorder(q, 0, altura - q.shape[0], 0, 0, cv2.BORDER_CONSTANT,
                                         value=(228, 228, 228)) for q in quadros])


def main() -> int:
    comp = json.loads((PASTA / "comparacao-pesel21.json").read_text(encoding="utf-8"))
    DESTINO.mkdir(parents=True, exist_ok=True)
    nomes = (("fase-1", "__C.jpg"), ("d97b937", "__C__depois.jpg"), ("agora", "__C__pesel21.jpg"))
    for base, d in comp["detalhe"].items():
        imgs = [cv2.imread(str(FINAIS / f"{base}{suf}")) for _n, suf in nomes]
        f = ALTURA / max(i.shape[0] for i in imgs)
        quadros = []
        for (nome, _s), img, chave in zip(nomes, imgs, ("fase1", "d97b937", "agora")):
            t = d[chave]["tamanho_mm"]
            quadros.append(_quadro(img, f, f"{base} - {nome}",
                                   f"{t[0] / 10:.1f} x {t[1] / 10:.1f} cm  escuro na beirada "
                                   f"{100 * d[chave]['beirada_escuro']:.1f}%"))
        cv2.imwrite(str(DESTINO / f"tres-{base}.jpg"), _lado_a_lado(quadros), [cv2.IMWRITE_JPEG_QUALITY, 88])
        if base.startswith("pesel_p021"):
            # o pe da pagina (ultimos 30%), de perto, na escala da pagina pronta / 2
            pes = []
            for (nome, _s), img in zip(nomes, imgs):
                a = img.shape[0]
                pe = img[int(a * 0.70):, :]
                pes.append(_quadro(pe, 0.5, f"Pesel 21 - {nome}", "o pe da pagina, de perto"))
            cv2.imwrite(str(DESTINO / f"perto-{base}.jpg"), _lado_a_lado(pes), [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(base)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
