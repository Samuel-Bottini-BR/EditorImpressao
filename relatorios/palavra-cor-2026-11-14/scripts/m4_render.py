"""Medida 4 (estudo D-701): grava, para cada página e resolução, a página como o programa a desenha
(core.pipeline.renderizar_pagina: o corpo da prévia, das miniaturas, da tela cheia, do Automático;
a 300 é igual ao PDF, conferido no m3) em Preto e branco:
  pb       sem caixinha (os pontos de letra são os pretos);
  letras   + "Letras com a cor delas";
  reduzir  + "Letras com a cor delas" + "Reduzir cores" (o de hoje).
Também grava o filtro Original ("original": a página preparada, para a cor do miolo da tinta).
Páginas: Livro de Horas 26 (o caso), Horas 13 (títulos vermelho e azul), Graduale 223 (rubricas
vermelhas e notas pretas). Livro novo de fábrica, caminho inteiro. Grava em _dados/m4/.

    python m4_render.py [dpi ...]
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
DADOS = AQUI.parent / "_dados"
os.environ["LOCALAPPDATA"] = str(DADOS / "local")
os.environ["APPDATA"] = str(DADOS / "local")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402

SAI = DADOS / "m4"
SAI.mkdir(parents=True, exist_ok=True)
PAGINAS = (__import__("os").environ.get("M4_PAGINAS") or "horas_p026,horas_p013,graduale_p223").split(",")


def main():
    from core import filtros as F
    from core import pipeline
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    dpis = [int(a) for a in sys.argv[1:]] or [110, 300]
    for nome in PAGINAS:
        copia = DADOS / f"{nome}.pdf"
        if not copia.exists():
            shutil.copyfile(RAIZ / "gabarito" / "paginas" / f"{nome}.pdf", copia)
        for dpi in dpis:
            for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
                g.clear()
            projeto = pipeline.analisar_projeto(Projeto(caminho_entrada=str(copia),
                                                        caminho_saida=str(SAI / "s.pdf"), nome=nome))
            pagina = projeto.paginas_ativas[0]
            pagina.filtro = F.PRETO_E_BRANCO
            doc = abrir_pdf(str(copia))
            try:
                pagina.filtro = F.ORIGINAL
                pagina.letras_com_a_cor = pagina.reduzir_cores = False
                img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                cv2.imwrite(str(SAI / f"{nome}_{dpi}_original.png"), img if img.ndim == 3 else
                            cv2.cvtColor(img, cv2.COLOR_GRAY2BGR))
                pagina.filtro = F.PRETO_E_BRANCO
                if __import__("os").environ.get("M4_SO_ORIGINAL"):
                    continue
                for jeito, campos in (("pb", {}), ("letras", {"letras_com_a_cor": True}),
                                      ("reduzir", {"letras_com_a_cor": True, "reduzir_cores": True})):
                    pagina.letras_com_a_cor = campos.get("letras_com_a_cor", False)
                    pagina.reduzir_cores = campos.get("reduzir_cores", False)
                    img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=dpi)
                    if img.ndim == 2:
                        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
                    cv2.imwrite(str(SAI / f"{nome}_{dpi}_{jeito}.png"), img)
                    print(nome, dpi, jeito, img.shape, flush=True)
            finally:
                doc.close()


if __name__ == "__main__":
    main()
