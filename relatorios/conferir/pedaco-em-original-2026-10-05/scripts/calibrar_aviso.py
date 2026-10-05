r"""Calibração do aviso "Sobrou papel em volta da figura" (core/ajustar_pedaco.py,
PAPEL_DEMAIS) e do ajuste, na Escola de Jesus 7 e na Opus Majus 20 do gabarito.

A página sem filtro (como a aba Marcar a usa), a 150 e a 300 DPI, com:
    - conf13: o retângulo da conferência 13 (o do implementador, 05/10);
    - verif: o que o verificador desenhou na janela (só Escola 7);
    - folgado: um retângulo com folga larga (pega texto e legenda);
    - por_dentro: um retângulo por dentro da pintura (nada a ajustar).
Grava calibracao.json e, a 150 DPI, cal-<pagina>-<caso>.jpg (laranja: o
retângulo como está; azul: o ajustado). Pasta de dados descartável.

Uso: .venv\Scripts\python.exe relatorios\conferir\pedaco-em-original-2026-10-05\scripts\calibrar_aviso.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

TRABALHO = Path(tempfile.mkdtemp(prefix="calibrar_aviso_"))
os.environ["LOCALAPPDATA"] = str(TRABALHO)
AQUI = Path(__file__).resolve().parents[1]
RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402

from core import pipeline  # noqa: E402
from core.ajustar_pedaco import PAPEL_DEMAIS, medir_folga  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

CASOS = {
    "escola_p007": {"conf13": (0.375, 0.378, 0.997, 0.932), "verif": (0.374, 0.379, 0.994, 0.931),
                    "folgado": (0.33, 0.36, 1.0, 0.975), "por_dentro": (0.40, 0.42, 0.95, 0.90)},
    "opusmajus_p020": {"conf13": (0.0014750830564784056, 0.0027804878048780495, 1.0, 0.9299024390243903),
                       "folgado": (0.0, 0.0, 1.0, 0.99)},
}


def main() -> None:
    saida: dict = {"PAPEL_DEMAIS": PAPEL_DEMAIS}
    for pid, caixas in CASOS.items():
        projeto = Projeto(caminho_entrada=str(RAIZ / "gabarito" / "paginas" / f"{pid}.pdf"), nome=pid)
        projeto.filtro_padrao = ORIGINAL
        projeto = pipeline.analisar_projeto(projeto)
        pagina = projeto.paginas_ativas[0]
        pagina.filtro = ORIGINAL
        doc = abrir_pdf(projeto.caminho_entrada)
        try:
            for dpi in (150, 300):
                img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                for nome, caixa in caixas.items():
                    t0 = time.perf_counter()
                    folga = medir_folga(img, caixa)
                    segundos = time.perf_counter() - t0
                    chave = f"{pid}/{nome}/{dpi}dpi"
                    if folga is None:
                        saida[chave] = None
                        continue
                    saida[chave] = {"retangulo": caixa,
                                    "ajustado": [round(float(v), 4) for v in folga.justa],
                                    "papel_em_volta": round(folga.fracao_de_papel, 4),
                                    "avisa": folga.muito, "segundos": round(segundos, 3)}
                    print(chave, saida[chave], flush=True)
                    if dpi == 150:
                        figura = img.copy()
                        a, l = figura.shape[:2]
                        for c, cor, g in ((caixa, (0, 110, 255), 3), (folga.justa, (200, 60, 0), 2)):
                            x0, y0, x1, y1 = (int(round(v * s)) for v, s in zip(c, (l, a, l, a)))
                            cv2.rectangle(figura, (x0, y0), (x1 - 1, y1 - 1), cor, g)
                        cv2.imwrite(str(AQUI / f"cal-{pid}-{nome}.jpg"), figura,
                                    [cv2.IMWRITE_JPEG_QUALITY, 85])
        finally:
            doc.close()
    (AQUI / "calibracao.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False),
                                          encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    finally:
        shutil.rmtree(TRABALHO, ignore_errors=True)
