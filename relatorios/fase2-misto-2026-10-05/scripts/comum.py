"""Peças comuns dos scripts da rodada do modo Misto (Fase 2, 05/10/2026).

O que faz: abre uma página do gabarito (o PDF de uma página em
D:\\programas\\EditorImpressao\\gabarito\\paginas, SOMENTE LEITURA) pelo mesmo
caminho do programa - core.pipeline.analisar_projeto e
core.pipeline.renderizar_pagina na resolução do PDF final (qualidade_dpi) -
e devolve a página preparada (dividida, cortada, endireitada) e a marcação de
gravura/letra/papel que o programa acha nela (garantir_selecao). É a mesma
imagem e a mesma marcação que o filtro recebe no "Confirmar e processar".

Antes de importar o programa, a pasta de dados (LOCALAPPDATA) passa para uma
pasta temporária: nada destes scripts escreve na pasta real do Samuel.

Seguro mudar: a lista de páginas. Arriscado mudar: o caminho de
imagem_preparada (tem de ser o do programa, senão a rodada mostra outra coisa).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]          # a worktree
GABARITO = Path(r"D:\programas\EditorImpressao\gabarito")  # somente leitura
PASTA = Path(__file__).resolve().parents[1]          # relatorios/fase2-misto-2026-10-05

# pasta de dados isolada (nunca a do Samuel)
_DADOS = Path(tempfile.gettempdir()) / "misto_localappdata"
_DADOS.mkdir(parents=True, exist_ok=True)
os.environ["LOCALAPPDATA"] = str(_DADOS)

if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# As páginas que o pedido da gerente cita, mais as outras do gabarito.
OBRIGATORIAS = ["palatino_p005", "palatino_p009", "escola_p007", "horas_p011",
                "horas_p013", "horas_p047", "opusmajus_p020", "graduale_p221",
                "graduale_p222", "opusmajus_p165"]


def todas_as_paginas() -> list[str]:
    """Os ids de todas as páginas do gabarito (lista.json), em ordem."""
    lista = json.loads((GABARITO / "lista.json").read_text(encoding="utf-8"))
    return sorted(lista["paginas"])


def caminho_pdf(pid: str) -> Path:
    return GABARITO / "paginas" / f"{pid}.pdf"


def abrir(pid: str, filtro: str):
    """(doc, projeto) da página do gabarito, analisada como o programa faz."""
    from core.pdf_io import abrir_pdf
    from core.pipeline import analisar_projeto
    from modelos import Projeto

    projeto = Projeto(caminho_entrada=str(caminho_pdf(pid)), nome=pid)
    projeto.filtro_padrao = filtro
    projeto = analisar_projeto(projeto)
    return abrir_pdf(projeto.caminho_entrada), projeto


def imagem_preparada(doc, projeto, pagina):
    """(img, selecao): a página pronta para o filtro e a marcação dela.

    Desenha a página com o filtro Original (o filtro devolve a imagem como
    chegou), pelo mesmo renderizar_pagina do programa, na resolução do PDF
    final: a detecção de gravura e letra roda igual (garantir_selecao é chamada
    antes de olhar o filtro) e fica guardada na página."""
    from core.filtros import ORIGINAL
    from core.pipeline import renderizar_pagina

    antes = pagina.filtro
    pagina.filtro = ORIGINAL
    try:
        img, _mono = renderizar_pagina(doc, projeto, pagina, dpi=projeto.qualidade_dpi)
    finally:
        pagina.filtro = antes
    return img, pagina.obter_selecao()


def soma(img) -> str:
    """sha256 dos pontos da imagem (com a forma), para provar "idêntica"."""
    import numpy as np

    h = hashlib.sha256()
    h.update(str(img.shape).encode())
    h.update(np.ascontiguousarray(img).tobytes())
    return h.hexdigest()


def reduzir(img, lado: int = 1600):
    """Cópia com o lado maior até `lado` (só para olhar; a conta é na cheia)."""
    import cv2

    a, l = img.shape[:2]
    f = lado / max(a, l)
    if f >= 1:
        return img
    return cv2.resize(img, (max(1, round(l * f)), max(1, round(a * f))), interpolation=cv2.INTER_AREA)


def gravar_jpg(caminho: Path, img, lado: int = 1600, qualidade: int = 88) -> Path:
    import cv2

    caminho.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(caminho), reduzir(img, lado), [cv2.IMWRITE_JPEG_QUALITY, qualidade])
    return caminho
