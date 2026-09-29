"""docTR pelo OnnxTR no item 1.3: so a DETECCAO (sem reconhecer texto).

Uso (ambiente de teste):
    .venv-ocr\\Scripts\\python.exe rodar_onnxtr.py [pagina ...]

- D1  detection_predictor('db_resnet50')
- D2  detection_predictor('fast_base')

O detector do docTR devolve caixas de PALAVRA. As linhas saem juntando as
palavras com o proprio montador de linhas do docTR (DocumentBuilder,
_resolve_lines: mesma altura, e quebra a linha quando o vao entre palavras
passa de 3,5% da largura da pagina). A pagina entra inteira: o docTR reduz
tudo para 1024 x 1024 por dentro (e o jeito de fabrica; ver Ressalvas).

Tempo: 3 rodadas por pagina (deteccao + juntar as linhas), mediana, com o
modelo ja carregado; o tempo de carregar o modelo vai a parte. Os modelos
baixam sozinhos para %USERPROFILE%\\.cache\\onnxtr (fora do projeto).
"""

from __future__ import annotations

import os
import sys
import time

import numpy as np
from onnxtr.models import detection_predictor
from onnxtr.models.builder import DocumentBuilder

import comum as C

CONFIGS = {"D1": "db_resnet50", "D2": "fast_base"}
RODADAS = int(os.environ.get("RODADAS", "3"))


def linhas_de_palavras(caixas: np.ndarray, w: int, h: int) -> list[dict]:
    """Palavras (relativas) -> linhas em pixels, pelo montador do docTR."""
    if len(caixas) == 0:
        return []
    rel = caixas[:, :4].astype(np.float64)
    grupos = DocumentBuilder()._resolve_lines(rel)
    linhas = []
    for idx in grupos:
        b = rel[idx]
        x0, y0 = b[:, 0].min() * w, b[:, 1].min() * h
        x1, y1 = b[:, 2].max() * w, b[:, 3].max() * h
        linhas.append({"poligono": [[x0, y0], [x1, y0], [x1, y1], [x0, y1]],
                       "palavras": len(idx),
                       "conf": float(caixas[idx, 4].mean())})
    return linhas


def main(paginas: list[str]) -> None:
    for config, arq in CONFIGS.items():
        t0 = time.perf_counter()
        det = detection_predictor(arch=arq)
        carga = time.perf_counter() - t0
        det([C.ler_imagem(paginas[0])])  # aquecimento (a 1a chamada do onnxruntime e mais lenta)
        for pagina in paginas:
            img = C.ler_imagem(pagina)
            h, w = img.shape[:2]
            tempos = []
            for _ in range(RODADAS):
                t0 = time.perf_counter()
                caixas = det([img])[0]
                linhas = linhas_de_palavras(caixas, w, h)
                tempos.append(time.perf_counter() - t0)
            C.gravar_linhas(config, pagina, linhas, tempos,
                            {"modelo": arq, "carga_modelo_s": carga, "palavras": int(len(caixas))})
            print(f"{config} {pagina:16s} {len(caixas):4d} palavras {len(linhas):4d} linhas "
                  f"{np.median(tempos):6.2f} s", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or C.PAGINAS)
