"""O modo Misto por linha de comando (Fase 2, 05/10/2026).

O Misto ainda NAO esta ligado ao programa (nem tela, nem projeto salvo: ligar
pede um campo novo e uma caixinha, decisao do Samuel). Este script monta o
resultado Misto de um PDF, pagina por pagina, pelo MESMO caminho do programa:

  1. core.pipeline.analisar_projeto (dividir, angulo, bordas), com as opcoes
     de fabrica da tela "O que fazer";
  2. core.pipeline.renderizar_pagina na resolucao do PDF final, com o filtro
     Original: a pagina preparada (dividida, cortada, endireitada) e a
     marcacao de gravura/letra/papel do programa (o detector do ScanTailor do
     item 1.2), guardada na pagina como no programa;
  3. core.misto.aplicar_misto: o Preto e branco so nas letras.

Uso (da pasta do projeto):

    .venv\\Scripts\\python.exe montar_misto.py LIVRO.pdf --saida PASTA
    .venv\\Scripts\\python.exe montar_misto.py LIVRO.pdf --paginas 5,9 --saida PASTA
        so essas paginas do PDF (contando de 1; a folha dividida da duas)
    --papel-creme   o papel de dentro das gravuras fica como no original (o
                    Misto puro do ScanTailor); de fabrica vai a branco
    --foto-cinza    as fotos em tons de cinza (como no Preto e branco); de
                    fabrica ficam como no original
    --forca N       a "Forca do preto" (0 a 100, 50 no meio)

Grava PASTA\\<nome>_f<folha>_<metade>.png (1 bit quando tudo saiu em preto e
branco). O PDF de entrada so e lido. A pasta de dados do programa
(LOCALAPPDATA) vai para uma pasta temporaria: o script nunca escreve na pasta
real do Samuel.

Seguro mudar: os nomes dos arquivos gravados. Arriscado mudar:
misto_da_pagina (tem de ser o caminho do programa, senao o Misto daqui nao e o
que o programa faria).
"""

from __future__ import annotations

import argparse
import os
import sys
import tempfile
import time
from pathlib import Path


def _isolar_pasta_de_dados() -> None:
    pasta = Path(tempfile.gettempdir()) / "montar_misto_localappdata"
    pasta.mkdir(parents=True, exist_ok=True)
    os.environ["LOCALAPPDATA"] = str(pasta)


def misto_da_pagina(doc, projeto, pagina, **opcoes):
    """(misto, monocromatica, preparada, selecao, segundos_do_misto) de uma
    pagina do projeto ja analisado. opcoes: as de core.misto.aplicar_misto
    (papel_da_gravura_branco, foto_em_cinza). O ajuste do Preto e branco e o
    da pagina (forca_preto, algoritmo_preto_branco) e o "Limpar pontinhos"
    dela (core.pipeline.pontinhos_da_pagina, com o DPI pedido; 06/10/2026)."""
    from core.filtros import ORIGINAL
    from core.misto import aplicar_misto
    from core.pipeline import pontinhos_da_pagina, renderizar_pagina

    antes = pagina.filtro
    pagina.filtro = ORIGINAL
    try:
        preparada, _mono = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        pagina.filtro = antes
    selecao = pagina.obter_selecao()
    inicio = time.perf_counter()
    misto, mono = aplicar_misto(
        preparada, selecao, pagina.forca_preto, pagina.algoritmo_preto_branco,
        pontinhos_da_pagina(projeto, pagina, preparada, projeto.qualidade_dpi),
        pagina.clareza_melhorar, pagina.intensidade_magico, **opcoes)
    return misto, mono, preparada, selecao, time.perf_counter() - inicio


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Monta o modo Misto de um PDF (linha de comando).")
    parser.add_argument("pdf")
    parser.add_argument("--saida", required=True)
    parser.add_argument("--paginas", default="", help="paginas do PDF, contando de 1 (ex.: 5,9)")
    parser.add_argument("--papel-creme", action="store_true")
    parser.add_argument("--foto-cinza", action="store_true")
    parser.add_argument("--forca", type=int, default=None)
    args = parser.parse_args(argv)

    _isolar_pasta_de_dados()
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import cv2

    from core.filtros import PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    pdf = Path(args.pdf)
    saida = Path(args.saida)
    saida.mkdir(parents=True, exist_ok=True)
    projeto = Projeto(caminho_entrada=str(pdf), nome=pdf.stem)
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto = analisar_projeto(projeto)
    pedidas = {int(p) - 1 for p in args.paginas.split(",") if p.strip()}
    opcoes = {"papel_da_gravura_branco": not args.papel_creme, "foto_em_cinza": args.foto_cinza}
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        for pagina in projeto.paginas_ativas:
            if pedidas and pagina.folha not in pedidas:
                continue
            if args.forca is not None:
                pagina.forca_preto = max(0, min(100, args.forca))
            misto, mono, _prep, _sel, segundos = misto_da_pagina(doc, projeto, pagina, **opcoes)
            nome = saida / f"{pdf.stem}_f{pagina.folha + 1:03d}_{pagina.metade}.png"
            cv2.imwrite(str(nome), misto)
            print(f"{nome.name}: {'1 bit' if mono else 'com tons/cor'}, Misto {segundos:.1f} s",
                  flush=True)
            del misto
    finally:
        doc.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
