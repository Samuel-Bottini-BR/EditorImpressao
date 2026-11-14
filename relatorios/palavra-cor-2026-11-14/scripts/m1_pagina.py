"""Medida 1 (estudo D-701): Livro de Horas 26 pelo caminho inteiro, como sai no PDF.

Livro novo de fábrica com só a página 26 (gabarito/paginas/horas_p026.pdf, cópia numa pasta de
dados própria), filtro Preto e branco, e três jeitos:
  a) só "Letras com a cor delas";
  b) "Letras com a cor delas" + "Reduzir cores" (o de hoje);
  c) o filtro Original (o scan, para comparar).
A página pronta vem de core.pipeline._pagina_pronta (o mesmo corpo do "Confirmar e processar").
Grava as imagens em _dados/m1/. Não muda nada do programa.

    .venv\\Scripts\\python.exe relatorios\\palavra-cor-2026-11-14\\scripts\\m1_pagina.py
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
(DADOS / "local").mkdir(parents=True, exist_ok=True)
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

from core import filtros as F  # noqa: E402
from core import pipeline  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

SAI = DADOS / "m1"
SAI.mkdir(parents=True, exist_ok=True)


def projeto_novo() -> Projeto:
    origem = RAIZ / "gabarito" / "paginas" / "horas_p026.pdf"
    copia = DADOS / "horas_p026.pdf"
    if not copia.exists():
        shutil.copyfile(origem, copia)
    for g in (pipeline._GEOMETRIAS, pipeline._CONTEUDOS, pipeline._TAMANHOS):
        g.clear()
    p = Projeto(caminho_entrada=str(copia), caminho_saida=str(SAI / "saida.pdf"), nome="h26")
    return pipeline.analisar_projeto(p)


def pronta(projeto, filtro, **campos):
    pagina = projeto.paginas_ativas[0]
    pagina.filtro = filtro
    for k in ("letras_com_a_cor", "reduzir_cores"):
        setattr(pagina, k, False)
    for k, v in campos.items():
        setattr(pagina, k, v)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        img, mono = pipeline._pagina_pronta(projeto, doc, projeto.folhas[pagina.folha], pagina,
                                            pipeline._FolhaDaVez(), 0)
    finally:
        doc.close()
    return img


def main():
    projeto = projeto_novo()
    print("qualidade_dpi", projeto.qualidade_dpi, "ordem", getattr(projeto, "ordem_do_preparo", None))
    for nome, filtro, campos in (
            ("original", F.ORIGINAL, {}),
            ("pb", F.PRETO_E_BRANCO, {}),
            ("letras", F.PRETO_E_BRANCO, {"letras_com_a_cor": True}),
            ("letras_reduzir", F.PRETO_E_BRANCO, {"letras_com_a_cor": True, "reduzir_cores": True})):
        img = pronta(projeto, filtro, **campos)
        cv2.imwrite(str(SAI / f"{nome}.png"), img)
        print(nome, img.shape, img.dtype)


if __name__ == "__main__":
    main()
