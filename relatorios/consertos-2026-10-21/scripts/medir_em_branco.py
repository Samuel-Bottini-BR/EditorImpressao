"""Mede o "Parece em branco" (core/analise.analisar_pagina) nas 87 folhas do
estudo do "Para revisar", e medidas alternativas, para o bug da Lista de bugs
de 08/10/2026: "aparece na Gladstone 18, que tem título, e não aparece no
Egenloff 12 nem na Rariora 8".

Cada folha é desenhada a 150 DPI (o DPI da análise, core.pipeline.DPI_ANALISE)
e medida inteira. Grava dados/em-branco.json. Somente leitura.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

RAIZ = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(RAIZ))

from core import analise  # noqa: E402

PAGINAS = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
SAIDA = Path(__file__).resolve().parents[1] / "dados" / "em-branco.json"


def medidas(img: np.ndarray) -> dict:
    cinza = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    a, l = cinza.shape
    miolo = cinza[int(a * .08):int(a * .92), int(l * .08):int(l * .92)]   # sem a beirada do scanner
    papel = float(np.percentile(miolo, 90))
    forte = miolo < 0.5 * papel
    n, _r, st, _c = cv2.connectedComponentsWithStats(forte.astype(np.uint8), 8)
    areas = st[1:, cv2.CC_STAT_AREA] if n > 1 else np.zeros(0)
    minimo = (150 / 100) ** 2 * 4                                       # tira pontinho
    pecas = int((areas >= minimo).sum())
    escuro = {f"abaixo_{int(f*100)}": round(float((miolo < f * papel).mean()), 6) for f in (0.25, 0.35, 0.45)}
    return {**escuro, "otsu": round(analise.fracao_de_tinta(img), 5),
            "forte_miolo": round(float(forte.mean()), 5),
            "pecas_fortes": pecas,
            "papel": round(papel, 1)}


def main() -> None:
    dados = {}
    for pdf in sorted(PAGINAS.glob("*.pdf")):
        with fitz.open(pdf) as doc:
            p = doc[0].get_pixmap(matrix=fitz.Matrix(150 / 72, 150 / 72), alpha=False)
        img = cv2.cvtColor(np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width, 3),
                           cv2.COLOR_RGB2BGR)
        dados[pdf.stem] = medidas(img)
    SAIDA.parent.mkdir(parents=True, exist_ok=True)
    SAIDA.write_text(json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in sorted(dados.items(), key=lambda kv: kv[1]["abaixo_35"])[:15]:
        print(k, v)


if __name__ == "__main__":
    main()
