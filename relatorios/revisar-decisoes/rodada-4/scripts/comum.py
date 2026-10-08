"""COPIA (rodada 4 das decisoes, 07/10/2026: roda com o ramo fase-1 de hoje, com o
conserto do desenho claro e o limpar pontinhos desligado de fabrica; dados novos em
<TRABALHO>/dados4, os das rodadas 1 a 3 ficam em <TRABALHO>/dados para comparar;
a pasta de dados do programa e isolada por pasta_de_dados_dos_scripts)
(rodada 3 das decisoes; usa a MESMA pasta de trabalho das rodadas 1 e 2)
(rodada 1 das decisoes do Para revisar, 06/10/2026) das pecas comuns do
estudo "quando uma pagina vai para Para revisar" (relatorios/revisar-criterios-2026-10-06).
Mudou so a pasta de trabalho (temporaria, propria desta rodada).

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

RAIZ = Path(r"D:\programas\EditorImpressao")
GABARITO = RAIZ / "gabarito"                                   # so leitura
ACERVO = Path(r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO\LIVROS PARA TESTE")
PASTA = Path(__file__).resolve().parents[1]                    # relatorios/revisar-decisoes/rodada-4
# Rodada 4: a pasta de trabalho passou para o D: (07/10, depois que o C: encheu);
# os dados das rodadas 1 a 3 foram copiados de %TEMP%/revisar_decisoes_rodada1.
TRABALHO = Path(os.environ.get(
    "REVISAR_TRABALHO", r"D:\programas\EditorImpressao-arquivos\revisar-decisoes-trabalho"))
DADOS = TRABALHO / "dados4"         # rodada 4: mascaras e imagens pesadas (fora do git)
DADOS_R3 = TRABALHO / "dados"       # o que as rodadas 1 a 3 gravaram (sem o conserto)
PAGINAS = TRABALHO / "paginas"      # PDFs de uma pagina tirados do acervo

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))
# Regra de 29/09 (CLAUDE.md): script nunca grava na pasta de dados de verdade.
# isolar_pasta_de_dados troca LOCALAPPDATA por uma pasta so desta rodada (aqui
# dentro da pasta de trabalho) e a apaga no fim, a nao ser que o programa tenha
# anotado algo no erros.log dela (ai o caminho e escrito no terminal).
from pasta_de_dados_dos_scripts import isolar_pasta_de_dados  # noqa: E402

PASTA_DE_DADOS = isolar_pasta_de_dados("revisar-rodada4", raiz=TRABALHO / "dados_do_programa")

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
# Rodada 2: o livro que nao entrou no estudo nem na rodada 1 (so leitura).
RIGHETTI = [6, 15, 30, 41, 50, 52, 54, 62, 64, 81, 94, 100]
for _n in RIGHETTI:
    EXTRAS[f"righetti_p{_n:03d}"] = ("Mario Righetti*.pdf", _n)

# Rodada 3: cinco livros novos do HD (D:\Livros para editar, so leitura), 6 paginas cada.
HD = Path(r"D:\Livros para editar")
LIVROS3 = {
    "antiphonal1547": (HD / "Antiphonal 1547.pdf", [6, 31, 46, 76, 192, 252]),
    "rariora": (HD / "Rariora musei besleriani quae olim basilius et michael rupertus besleri.pdf",
                [8, 99, 155, 169, 211, 365]),
    "egenloff": (HD / "Egenloff15271880ModelbuchWHZ_231103_053749.pdf", [3, 7, 12, 47, 121, 131]),
    "gladstone": (HD / "Gladstone_Chaves_de_Melo_Novo_Manual_de_Análise_Sintática_1954.pdf",
                  [5, 18, 55, 96, 116, 136]),
    "camoes": (HD / "HISTÓRIA" /
               "Luiz de Camões levantando o seu monumento ou A Historia de Portugal justificada pelos Lusiadas.pdf",
               [6, 9, 11, 27, 66, 104]),
}
for _livro, (_arq, _pags) in LIVROS3.items():
    for _n in _pags:
        EXTRAS[f"{_livro}_p{_n:03d}"] = (str(_arq), _n)


def paginas_do_gabarito() -> list[str]:
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
    return sorted(lista["paginas"])


def todas() -> list[str]:
    return paginas_do_gabarito() + list(EXTRAS)


def as_89() -> list[str]:
    """Rodada 4: as 57 paginas do estudo (59 com as metades do Siebmacher) e as
    30 da rodada 3. O Righetti (rodada 2) fica de fora."""
    return [p for p in todas() if not p.startswith("righetti")]


def caminho_pdf(pid: str) -> Path:
    """O PDF de uma pagina: o do gabarito, ou tirado do livro do acervo."""
    if pid in EXTRAS:
        padrao, numero = EXTRAS[pid]
        destino = PAGINAS / f"{pid}.pdf"
        if not destino.exists():
            import fitz

            livro = Path(padrao) if Path(padrao).is_absolute() else sorted(ACERVO.glob(padrao))[0]
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
    doc = abrir_pdf(projeto.caminho_entrada)
    if pid.startswith("righetti"):
        _girar_e_dividir(doc, projeto, filtro)
    elif pid.startswith("siebmacher") and not projeto.folhas[0].dividir:
        _dividir(doc, projeto, filtro)
    return doc, projeto


def _dividir(doc, projeto, filtro) -> None:
    """Rodada 4: no fase-1 de hoje (dividir do ScanTailor de fabrica) a folha
    dupla do Siebmacher 7 e 9 NAO e mais dividida (sai uma pagina so). Para
    comparar com as respostas das rodadas 1 a 3 (feitas nas metades), a folha e
    dividida aqui como a pessoa faria na aba "Onde cortar", na lombada achada
    pelo detector de sempre (core.dividir.detectar_lombada)."""
    from core.dividir import detectar_lombada
    from core.pdf_io import pagina_para_array
    from core.pipeline import DPI_ANALISE
    from modelos import ConfigPagina

    folha = projeto.folhas[0]
    lombada = detectar_lombada(pagina_para_array(doc, 0, dpi=DPI_ANALISE))
    folha.dividir = True
    folha.posicao_corte = lombada.posicao
    folha.confianca_corte = lombada.confianca
    projeto.paginas = [ConfigPagina(indice=i, folha=0, metade=m, filtro=filtro)
                       for i, m in enumerate(("esquerda", "direita"))]


def _girar_e_dividir(doc, projeto, filtro) -> None:
    """Righetti: cada folha do PDF tem DUAS paginas deitadas. O que a pessoa
    faria na tela: "Girar 1/4 a esquerda" (rotacao 270, conferido olhando) e
    dividir a folha na lombada. O giro do programa (core/girar) nao refaz a
    divisao sozinho, entao aqui a lombada e achada na folha ja girada pelo
    mesmo detector da analise (core.dividir.detectar_lombada) e a folha vira
    duas paginas, esquerda e direita."""
    from core.dividir import detectar_lombada
    from core.endireitar import girar_90
    from core.pdf_io import pagina_para_array
    from core.pipeline import DPI_ANALISE
    from modelos import ConfigPagina

    folha = projeto.folhas[0]
    folha.rotacao = 270
    img = girar_90(pagina_para_array(doc, 0, dpi=DPI_ANALISE), 270)
    lombada = detectar_lombada(img)
    folha.dividir = True
    folha.e_paisagem = True
    folha.posicao_corte = lombada.posicao
    folha.confianca_corte = lombada.confianca
    projeto.paginas = [ConfigPagina(indice=i, folha=0, metade=m, filtro=filtro)
                       for i, m in enumerate(("esquerda", "direita"))]


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
