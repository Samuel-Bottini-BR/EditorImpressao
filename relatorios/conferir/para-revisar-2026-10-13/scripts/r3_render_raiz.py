"""20/10/2026: desenha uma pagina como LIVRO NOVO em Preto e branco + "So as letras" (Guardar a tinta
forte), a 300 DPI (a resolucao do PDF), com o codigo de OUTRA pasta (para comparar o programa de
hoje com o ramo). So le; pasta de dados isolada no trabalho/. Nao muda o programa.

Uso: python r3_render_raiz.py <raiz do codigo> <pdf> <pagina 1..> <nome da saida>"""
import os
import sys
from pathlib import Path

raiz, pdf, pagina, nome = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
BASE = Path(__file__).resolve().parent.parent
dados = BASE / "trabalho" / "dados_render"
os.environ["LOCALAPPDATA"] = str(dados / "local")
os.environ["USERPROFILE"] = str(dados / "home")
sys.path.insert(0, raiz)

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import pipeline as P  # noqa: E402
from core.filtros import PRETO_E_BRANCO  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

projeto = Projeto(caminho_entrada=pdf, nome=Path(pdf).stem[:24])
projeto.filtro_padrao = PRETO_E_BRANCO
projeto = P.analisar_projeto(projeto)
projeto.misto_so_as_letras = True
doc = abrir_pdf(pdf)
pg = projeto.paginas[pagina - 1]
pg.filtro = PRETO_E_BRANCO
img = P.renderizar_pagina(doc, projeto, pg, dpi=300)
img = np.asarray(img[0] if isinstance(img, tuple) else img)
saida = BASE / "trabalho" / "desenhos" / f"{nome}.png"
cv2.imencode(".png", cv2.cvtColor(img, cv2.COLOR_RGB2BGR) if img.ndim == 3 else img)[1].tofile(str(saida))
print("codigo:", raiz, "| ordem:", getattr(projeto, "ordem_do_preparo", None), "| avisos:", list(pg.alertas), "->", saida.name)
