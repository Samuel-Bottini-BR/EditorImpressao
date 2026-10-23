"""Mede o tempo ate a PRIMEIRA previa de uma pagina que ainda nao tem marcacao
(gravura, letra e papel), no filtro de fabrica (Original).

Para que: a regra 6 do plano (nenhum item deixa o programa mais lento). O
conserto de 13/10 (commit 027e50d) procurava a marcacao na pagina do tamanho do
PDF ANTES de mostrar a previa e custava 0,8 s a mais na primeira previa de cada
pagina. A gerente mandou tirar a espera da frente: a busca passou a ser por
tras (core.pipeline.acertar_no_tamanho_do_pdf). Este script mostra o tempo da
previa em qualquer copia do codigo, para comparar a de hoje com a de antes.

Uso:  python tempo_da_primeira_previa.py <pasta do codigo> [repeticoes]
      (a pasta do codigo e a raiz de uma copia do projeto: a desta worktree,
      ou uma copia de um commit antigo tirada com `git archive`)

Por pagina: um projeto NOVO a cada medida (sem marcacao guardada), a analise
fora do relogio, e o relogio so em core.pipeline.renderizar_pagina(dpi=110).
Fica o MENOR tempo das repeticoes (o que menos sofreu com o resto do PC).
Pasta de dados do programa isolada; os PDFs sao so lidos.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
CODIGO = Path(sys.argv[1]).resolve()
REPETICOES = int(sys.argv[2]) if len(sys.argv) > 2 else 3
sys.path.insert(0, str(CODIGO))

from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

isolar_pasta_de_dados("tempo-da-primeira-previa", raiz=AQUI.parents[1] / "saida_teste" / "dados_dos_scripts")

from core import pipeline as P  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from modelos import Projeto  # noqa: E402

GABARITO = AQUI.parents[1] / "gabarito" / "paginas"
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho\paginas")
PAGINAS = ["marial_p007", "palatino_p007", "boecio_p007", "horas_p011", "graduale_p221",
           "escola_p007", "opusmajus_p020", "camoes_p027"]


def pdf_de(pid: str) -> str:
    do_acervo = ACERVO / f"{pid}.pdf"
    return str(do_acervo if do_acervo.exists() else GABARITO / f"{pid}.pdf")


def uma(caminho: str) -> float:
    projeto = Projeto(caminho_entrada=caminho, nome="x")
    projeto.filtro_padrao = ORIGINAL
    projeto = P.analisar_projeto(projeto)
    doc = abrir_pdf(caminho)
    t0 = time.perf_counter()
    P.renderizar_pagina(doc, projeto, projeto.paginas[0], dpi=110)
    t = time.perf_counter() - t0
    doc.close()
    return t


tempos = {}
uma(pdf_de(PAGINAS[0]))                       # aquece (abre o detector, cache do disco)
for pid in PAGINAS:
    caminho = pdf_de(pid)
    uma(caminho)
    tempos[pid] = round(min(uma(caminho) for _ in range(REPETICOES)), 3)
    print(f"{pid:18s} {tempos[pid]:6.2f} s", flush=True)
media = sum(tempos.values()) / len(tempos)
print(f"media das {len(tempos)} paginas: {media:.2f} s   (codigo: {CODIGO})")
print(json.dumps({"codigo": str(CODIGO), "media": round(media, 3), "paginas": tempos}))
