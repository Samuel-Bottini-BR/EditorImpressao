r"""Pecas comuns dos scripts da conferencia 11 (05/10/2026, formulario conferir-aqui-11.html).

PROTOTIPO, NAO E O PROGRAMA: estes scripts importam o codigo do programa (ramo fase2-misto) e
fazem as variacoes "como ficaria" AQUI, sem mudar nenhum arquivo do programa (core/, ui/,
modelos.py, projetos.py).

O que faz: abre uma pagina do gabarito (D:\programas\EditorImpressao\gabarito\paginas, SOMENTE
LEITURA) pelo mesmo caminho do programa (core.pipeline.analisar_projeto e renderizar_pagina na
resolucao do PDF final, com o filtro Original) e guarda num cache a pagina preparada e a marcacao
que o programa achou nela (gravura/letra/papel), para os outros scripts nao refazerem a deteccao.

Pasta de dados do programa (LOCALAPPDATA) e o cache: numa pasta de teste propria (variavel
CONF11_DADOS, ou %TEMP%\conf11_dados) - nunca a pasta real do Samuel.

Seguro mudar: a pasta do cache. Arriscado: imagem_preparada (tem de ser o caminho do programa).
"""
from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]                 # a worktree misto
GABARITO = Path(r"D:\programas\EditorImpressao\gabarito")   # somente leitura
AQUI = Path(__file__).resolve().parents[1]                  # relatorios/conferencia-11-2026-10-05

DADOS = Path(os.environ.get("CONF11_DADOS") or (Path(tempfile.gettempdir()) / "conf11_dados"))
(DADOS / "localappdata").mkdir(parents=True, exist_ok=True)
(DADOS / "cache").mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(DADOS / "localappdata")

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))


def preparada(pid: str):
    """(img, selecao, ajustes) da pagina `pid` do gabarito, do cache ou feita agora.
    ajustes: os da pagina (forca_preto, algoritmo_preto_branco, despeckle, clareza, intensidade)."""
    import cv2

    from core.selecao import Selecao

    png = DADOS / "cache" / f"{pid}.png"
    js = DADOS / "cache" / f"{pid}.json"
    if png.exists() and js.exists():
        dados = json.loads(js.read_text(encoding="utf-8"))
        return cv2.imread(str(png), cv2.IMREAD_UNCHANGED), Selecao.de_lista(dados["selecao"]), dados["ajustes"]

    from core.filtros import ORIGINAL, PRETO_E_BRANCO
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto, renderizar_pagina
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(GABARITO / "paginas" / f"{pid}.pdf"), nome=pid)
    projeto.filtro_padrao = PRETO_E_BRANCO
    projeto = analisar_projeto(projeto)
    doc = abrir_pdf(projeto.caminho_entrada)
    try:
        pagina = projeto.paginas_ativas[0]
        pagina.filtro = ORIGINAL
        img, _mono = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
        selecao = pagina.obter_selecao()
        ajustes = {"forca_preto": pagina.forca_preto, "algoritmo_pb": pagina.algoritmo_preto_branco,
                   "despeckle": pagina.despeckle, "clareza": pagina.clareza_melhorar,
                   "intensidade": pagina.intensidade_magico}
    finally:
        doc.close()
    cv2.imwrite(str(png), img)
    js.write_text(json.dumps({"selecao": selecao.para_lista(), "ajustes": ajustes}), encoding="utf-8")
    return img, selecao, ajustes


def copia(selecao):
    """Uma copia independente da marcacao (para acrescentar zonas sem mexer na original)."""
    from core.selecao import Selecao

    return Selecao.de_lista(selecao.para_lista())
