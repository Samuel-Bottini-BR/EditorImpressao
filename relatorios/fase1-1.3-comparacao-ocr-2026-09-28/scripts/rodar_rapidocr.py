"""PP-OCR pelo RapidOCR no item 1.3: so a DETECCAO (use_det, sem cls nem rec).

Uso (ambiente de teste):
    .venv-ocr\\Scripts\\python.exe rodar_rapidocr.py [pagina ...]

- P1  PP-OCRv5 servidor (ch_PP-OCRv5_det_server)
- P2  PP-OCRv5 movel    (ch_PP-OCRv5_det_mobile)
- P3  PP-OCRv6 pequeno  (o detector padrao do RapidOCR 3.9.2; extra, fora da pesquisa)

Ajuste da pesquisa: o RapidOCR reduz a pagina para no maximo 2000 px de lado
(Global.max_side_len); aqui o teto sobe para 3000, para a pagina entrar na
resolucao de trabalho (a maior tem 2774 px) e a letra pequena nao sumir.
Det.limit_side_len/limit_type ficam no padrao (min 736: so aumenta pagina pequena).

Tempo: 3 rodadas por pagina, mediana, com o modelo ja carregado.
Os modelos baixam sozinhos para dentro do pacote rapidocr (no .venv-ocr).
"""

from __future__ import annotations

import os
import sys
import time

import cv2
import numpy as np
from rapidocr import RapidOCR
from rapidocr.utils.typings import LangDet, ModelType, OCRVersion

import comum as C

CONFIGS = {
    "P1": {"Det.ocr_version": OCRVersion.PPOCRV5, "Det.model_type": ModelType.SERVER, "Det.lang_type": LangDet.CH},
    "P2": {"Det.ocr_version": OCRVersion.PPOCRV5, "Det.model_type": ModelType.MOBILE, "Det.lang_type": LangDet.CH},
    "P3": {"Det.ocr_version": OCRVersion.PPOCRV6, "Det.model_type": ModelType.SMALL, "Det.lang_type": LangDet.CH},
}
RODADAS = int(os.environ.get("RODADAS", "3"))
LADO_MAXIMO = int(os.environ.get("LADO_MAXIMO", "3000"))


def main(paginas: list[str], configs: list[str]) -> None:
    for config in configs:
        params = dict(CONFIGS[config])
        params.update({"Global.max_side_len": LADO_MAXIMO, "Global.use_cls": False,
                       "Global.use_rec": False, "Global.log_level": "warning"})
        t0 = time.perf_counter()
        motor = RapidOCR(params=params)
        carga = time.perf_counter() - t0
        motor(cv2.imread(str(C.caminho_imagem(paginas[0]))), use_det=True, use_cls=False, use_rec=False)
        for pagina in paginas:
            bgr = cv2.imread(str(C.caminho_imagem(pagina)))
            tempos = []
            for _ in range(RODADAS):
                t0 = time.perf_counter()
                res = motor(bgr, use_det=True, use_cls=False, use_rec=False)
                tempos.append(time.perf_counter() - t0)
            caixas = res.boxes if res.boxes is not None else np.zeros((0, 4, 2))
            scores = getattr(res, "scores", None)
            linhas = [{"poligono": np.asarray(b, float).tolist()} for b in caixas]
            nome = config if LADO_MAXIMO == 3000 else f"{config}_{LADO_MAXIMO}"
            C.gravar_linhas(nome, pagina, linhas, tempos,
                            {"modelo": str(params["Det.ocr_version"].value) + " " + params["Det.model_type"].value,
                             "carga_modelo_s": carga, "lado_maximo": LADO_MAXIMO})
            print(f"{nome} {pagina:16s} {len(linhas):4d} linhas {np.median(tempos):6.2f} s", flush=True)


if __name__ == "__main__":
    args = sys.argv[1:]
    configs = [a for a in args if a in CONFIGS] or list(CONFIGS)
    paginas = [a for a in args if a not in CONFIGS] or C.PAGINAS
    main(paginas, configs)
