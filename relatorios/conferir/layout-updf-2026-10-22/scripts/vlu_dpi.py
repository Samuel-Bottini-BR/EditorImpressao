"""Tinta da página 7 do Boécio desenhada a 150 DPI (a tela cheia) e a 300 DPI (o PDF), reduzida ao
mesmo tamanho, em vários jeitos do Preto e branco. Só core/. Uso: python vlu_dpi.py"""
import os
import sys
from dataclasses import replace
from pathlib import Path

CODIGO = Path(r"D:\programas\EditorImpressao\.claude\worktrees\layout-4a7")
TRAB = CODIGO / "saida_teste" / "vlu_trab"
os.environ["LOCALAPPDATA"] = str(TRAB / "dados")
os.environ["TEMP"] = os.environ["TMP"] = str(TRAB / "tmp")
sys.path.insert(0, str(CODIGO))
os.chdir(CODIGO)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.pipeline import analisar_projeto, renderizar_pagina  # noqa: E402
from modelos import Projeto  # noqa: E402

livro = str(TRAB / "Boecio (copia).pdf")
projeto = analisar_projeto(Projeto(caminho_entrada=livro, nome="b"))
p = projeto.paginas[6]
casos = {
    "P&B de fábrica": replace(p, filtro=PRETO_E_BRANCO),
    "P&B + Wolf do ScanTailor": replace(p, filtro=PRETO_E_BRANCO, algoritmo_preto_branco="st_wolf"),
    "P&B + Só as letras + Limpeza média + Wolf do ST": replace(
        p, filtro=PRETO_E_BRANCO, algoritmo_preto_branco="st_wolf", limpar_pontinhos="st_normal",
        misto_so_as_letras=True),
    "P&B + Otsu do ScanTailor": replace(p, filtro=PRETO_E_BRANCO, algoritmo_preto_branco="st_otsu"),
}
doc = abrir_pdf(livro)
for nome, pg in casos.items():
    try:
        for _ in range(2):
            a, _m = renderizar_pagina(doc, projeto, replace(pg, alertas=list(pg.alertas)), dpi=150)
        b, _m = renderizar_pagina(doc, projeto, replace(pg, alertas=list(pg.alertas)), dpi=300)
    except TypeError as e:
        print(nome, "erro", e)
        continue
    g = lambda x: x if x.ndim == 2 else cv2.cvtColor(x, cv2.COLOR_RGB2GRAY)  # noqa: E731
    a, b = g(a), g(b)
    b2 = cv2.resize(b, (a.shape[1], a.shape[0]), interpolation=cv2.INTER_AREA)
    print(f"{nome}: tinta a 150 DPI {100 * (a < 128).mean():.2f}% ; a 300 DPI reduzida {100 * (b2 < 128).mean():.2f}%"
          f" ; 300 DPI no tamanho dela {100 * (b < 128).mean():.2f}%  ({a.shape} x {b.shape})")
doc.close()
