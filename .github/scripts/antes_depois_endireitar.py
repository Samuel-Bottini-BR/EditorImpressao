"""Antes/depois do item 2.2 (G6, endireitar antes de cortar) nas paginas-gabarito.

Usado pelo job "antes_depois" do .github/workflows/testes-windows.yml (so com
workflow_dispatch e "antes_depois" marcado). Nao e parte do programa: nada aqui
e importado por core/, ui/ ou tests/.

    python .github/scripts/antes_depois_endireitar.py --saida prints

O que faz, com o codigo do ramo que o job trocou (fase-1 = antes;
fase2-endireitar-2 = depois):
  para cada pagina-gabarito de PAGINAS (o PDF de uma pagina em gabarito/paginas/,
  que vem do ramo dados-de-teste), cria um LIVRO NOVO como o Kaique criaria
  (Projeto com o caminho do PDF; no ramo do G6 isso ja nasce "endireitar_antes"),
  com o filtro Original (so se ve a geometria, nao o filtro) e sem detectar
  gravura, analisa e grava, por pagina de saida:
    <chave>-<metade>-preparada.png  a pagina como vai sair (girada, cortada,
                                    endireitada), a 150 DPI;
    <chave>-<metade>-bordas.png     a imagem da aba Bordas/Cortar (sem corte).
  Escreve no log o angulo, o corte e a ordem usados (o ramo prints-testes e so
  de imagens: os numeros ficam no log do job).

Seguro mudar: a lista PAGINAS, o DPI das imagens. Arriscado: trocar o filtro
(a comparacao deixaria de ser so de geometria); reaproveitar o mesmo Projeto
entre paginas (a geometria guardada de uma vazaria para a outra).
"""

from __future__ import annotations

import argparse
import os
import sys
import traceback
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]

# Item 2.2 do gabarito/lista.json (graduale_p221, escola_p007) e as outras que a
# gerente pediu em 09/10/2026 para a conferencia do G6.
PAGINAS = (
    "graduale_p221", "graduale_p222", "escola_p007", "escola_p035",
    "siebmacher_p007", "siebmacher_p009", "palatino_p066", "horas_p011",
    "horas_p027", "opusmajus_p020", "boecio_p008", "marial_p007",
)
DPI = 150


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--saida", default="prints")
    p.add_argument("--raiz", default=str(RAIZ), help="pasta do programa (so para testar fora do job)")
    a = p.parse_args()
    raiz = Path(a.raiz).resolve()
    saida = Path(a.saida).resolve()
    saida.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    sys.path.insert(0, str(raiz))
    os.chdir(raiz)

    import cv2
    from core import pipeline
    from core.filtros import ORIGINAL
    from core.pdf_io import abrir_pdf
    from modelos import Projeto

    print(f"programa testado: {os.environ.get('TESTADO_RAMO', '?')} {os.environ.get('TESTADO_SHA', '?')}")
    erros = 0
    for chave in PAGINAS:
        pdf = raiz / "gabarito" / "paginas" / f"{chave}.pdf"
        if not pdf.exists():
            print(f"{chave}: FALTA {pdf}")
            erros += 1
            continue
        try:
            pipeline._GEOMETRIAS.clear()
            projeto = Projeto(caminho_entrada=str(pdf), nome=chave)
            projeto.filtro_padrao = ORIGINAL
            projeto.detectar_regioes = False
            projeto = pipeline.analisar_projeto(projeto)
            ordem = getattr(projeto, "ordem_do_preparo", "(sem o campo: cortar_antes)")
            doc = abrir_pdf(projeto.caminho_entrada)
            try:
                for pagina in projeto.paginas_ativas:
                    img, _ = pipeline.renderizar_pagina(doc, projeto, pagina, dpi=DPI)
                    bordas = pipeline.renderizar_pagina_para_recorte(doc, projeto, pagina, dpi=DPI)
                    nome = f"{chave}-{pagina.metade}"
                    cv2.imwrite(str(saida / f"{nome}-preparada.png"), img)
                    cv2.imwrite(str(saida / f"{nome}-bordas.png"), bordas)
                    medidos = pipeline.angulos_medidos(projeto, pagina)
                    desenho = getattr(pagina, "geometria_das_zonas", None)
                    print(f"{nome}: ordem={ordem} preparada={img.shape[1]}x{img.shape[0]} "
                          f"bordas={bordas.shape[1]}x{bordas.shape[0]} "
                          f"angulo={pipeline.angulo_da_pagina(projeto, pagina)} medidos={medidos} "
                          f"recorte_a_mao={pagina.recorte} geometria={desenho}")
            finally:
                doc.close()
        except Exception:
            erros += 1
            print(f"{chave}: ERRO\n{traceback.format_exc()}")
    print(f"fim: {len(PAGINAS)} paginas, {erros} com erro")
    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
