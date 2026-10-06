"""Pecas comuns da medida "Misto: desenho claro apagado" (06/10/2026).

COPIA de relatorios/revisar-criterios-2026-10-06/scripts/comum.py (o estudo
nao foi mudado). Diferencas: RAIZ e a worktree "consertos" (o codigo que roda
e o do ramo misto-desenho-apagado); TRABALHO fica dentro desta pasta, em
trabalho/ (fora do git pelo .gitignore de relatorios/conferir).

Texto original:

Abre uma pagina (do gabarito, ou uma pagina tirada de um livro do acervo para
um PDF de uma pagina so, numa pasta temporaria) pelo MESMO caminho do
programa: core.pipeline.analisar_projeto e core.pipeline.renderizar_pagina na
resolucao do PDF final. Nada aqui muda o programa; os livros do acervo e o
gabarito sao so lidos.

A pasta de dados do programa (LOCALAPPDATA) vai para uma pasta temporaria
antes de importar o programa: nada destes scripts escreve na pasta do Samuel.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(r"D:\programas\EditorImpressao\.claude\worktrees\consertos")
GABARITO = RAIZ / "gabarito"                                   # so leitura
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
PASTA = Path(__file__).resolve().parents[1]                    # relatorios/revisar-criterios-2026-10-06
TRABALHO = Path(os.environ.get("MISTO_TRABALHO", PASTA / "trabalho"))
DADOS = TRABALHO / "dados"          # mascaras e imagens pesadas (fora do git)
PAGINAS = TRABALHO / "paginas"      # PDFs de uma pagina tirados do acervo

_LOCAL = TRABALHO / "localappdata"
_LOCAL.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_LOCAL)
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Paginas a mais, do acervo (pagina contada a partir de 1, como no leitor de PDF).
# Escolhidas olhando miniaturas: musica com capitular, diagrama, tabela,
# gravura com texto, moldura, texto puro, calendario, iluminura.
EXTRAS = {
    "antiphon_p088": ("Antiphon_25.pdf", 88),
    "antiphon_p260": ("Antiphon_25.pdf", 260),
    "ljs47_p026": ("ljs47.pdf", 26),
    "ljs47_p049": ("ljs47.pdf", 49),
    "ljs47_p064": ("ljs47.pdf", 64),
    "ljs47_p103": ("ljs47.pdf", 103),
    "matematica_p032": ("Matem*tica Para vencer.pdf", 32),
    "matematica_p072": ("Matem*tica Para vencer.pdf", 72),
    "rhetorica_p034": ("Rhetorica Christiana*.pdf", 34),
    "rhetorica_p129": ("Rhetorica Christiana*.pdf", 129),
    "rhetorica_p160": ("Rhetorica Christiana*.pdf", 160),
    "palatino_p076": ("Giovambattista Palatino*.pdf", 76),
    "palatino_p104": ("Giovambattista Palatino*.pdf", 104),
    "palatino_p113": ("Giovambattista Palatino*.pdf", 113),
    "horas_p016": ("Livro de Horas*.pdf", 16),
    "horas_p175": ("Livro de Horas*.pdf", 175),
    "escola_p113": ("Na escola de Jesus*.pdf", 113),
    "escola_p197": ("Na escola de Jesus*.pdf", 197),
    "graduale_p269": ("Graduale*.pdf", 269),
    "graduale_p588": ("Graduale*.pdf", 588),
    "marial_p454": ("Marial de sermoens*.pdf", 454),
    "marial_p840": ("Marial de sermoens*.pdf", 840),
    "cursus_p003": ("Cursus philosophicus*.pdf", 3),
    "cursus_p314": ("Cursus philosophicus*.pdf", 314),
    "pesel_p021": ("POINTS*.pdf", 21),
}


def paginas_do_gabarito() -> list[str]:
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
    return sorted(lista["paginas"])


def todas() -> list[str]:
    return paginas_do_gabarito() + list(EXTRAS)


def caminho_pdf(pid: str) -> Path:
    """O PDF de uma pagina: o do gabarito, ou tirado do livro do acervo."""
    if pid in EXTRAS:
        padrao, numero = EXTRAS[pid]
        destino = PAGINAS / f"{pid}.pdf"
        if not destino.exists():
            import fitz

            livro = sorted(ACERVO.glob(padrao))[0]
            PAGINAS.mkdir(parents=True, exist_ok=True)
            with fitz.open(livro) as origem, fitz.open() as novo:
                novo.insert_pdf(origem, from_page=numero - 1, to_page=numero - 1)
                novo.save(destino)
        return destino
    return GABARITO / "paginas" / f"{pid}.pdf"


def abrir(pid: str, filtro: str):
    """(doc, projeto) da pagina, analisada como o programa faz."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(caminho_pdf(pid)), nome=pid)
    projeto.filtro_padrao = filtro
    projeto = analisar_projeto(projeto)
    return abrir_pdf(projeto.caminho_entrada), projeto


def reduzir(img, lado: int = 1400):
    import cv2

    a, l = img.shape[:2]
    f = lado / max(a, l)
    if f >= 1:
        return img
    return cv2.resize(img, (max(1, round(l * f)), max(1, round(a * f))), interpolation=cv2.INTER_AREA)


def gravar_jpg(caminho: Path, img, lado: int = 1400, qualidade: int = 85) -> Path:
    import cv2

    caminho.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(caminho), reduzir(img, lado), [cv2.IMWRITE_JPEG_QUALITY, qualidade])
    return caminho
