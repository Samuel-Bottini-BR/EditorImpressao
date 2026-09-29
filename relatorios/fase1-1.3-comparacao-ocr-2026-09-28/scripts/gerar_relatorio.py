"""Monta o relatorio do 1.3: preenche modelo-relatorio.md com as tabelas e as imagens.

Dois passos, porque o relatorio.gravar do programa precisa da biblioteca
`markdown`, que so esta no .venv do programa (e nao se instala nada nele):

    .venv-ocr\\Scripts\\python.exe gerar_relatorio.py montar
        -> grava o texto final em scripts\\relatorio-montado.md
    .venv\\Scripts\\python.exe relatorios\\fase1-1.3-comparacao-ocr-2026-09-28\\scripts\\gerar_relatorio.py gravar
        -> relatorio.gravar(...) grava .md, .html e .pdf na pasta do relatorio

Seguro mudar: a ordem das imagens. Os numeros vem de resultados.json e pares.json.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
NOME = PASTA.name  # fase1-1.3-comparacao-ocr-2026-09-28
MONTADO = AQUI / "relatorio-montado.md"

ORDEM_IMAGENS = [
    "palatino_p005", "palatino_p007", "palatino_p009", "palatino_p010", "palatino_p057",
    "escola_p007", "escola_p035", "horas_p011", "horas_p013", "horas_p026", "horas_p027",
    "horas_p047", "opusmajus_p003", "opusmajus_p011", "opusmajus_p020", "opusmajus_p165",
    "opusmajus_p256", "rhetorica_p018", "siebmacher_p009", "graduale_p221", "graduale_p222",
    "graduale_p223",
]


LIVROS = {"palatino": "Palatino", "escola": "Escola", "horas": "Horas", "opusmajus": "Opus Majus",
          "rhetorica": "Rhetorica", "siebmacher": "Siebmacher", "graduale": "Graduale"}
NOMES = {pg: f"{LIVROS[pg.split('_p')[0]]} {int(pg.split('_p')[1])}" for pg in ORDEM_IMAGENS}


def _virgula(tabela: str) -> str:
    """Numero com ponto -> com virgula (portugues), so nas tabelas."""
    return re.sub(r"(\d)\.(\d)", r"\1,\2", tabela)


def montar() -> None:
    sys.path.insert(0, str(AQUI))
    import tabelas

    t = tabelas.tabelas_relatorio()
    texto = (AQUI / "modelo-relatorio.md").read_text(encoding="utf-8")
    for chave, tabela in t.items():
        texto = texto.replace("{{" + chave + "}}", _virgula(tabela))
    # HTML cru, e nao ![](...): o PDF (Story do PyMuPDF) ENCOLHE a imagem que
    # nao cabe no fim da pagina, e metade das folhas saia minuscula (medido em
    # 28/09). Com "page-break-before" cada folha comeca numa pagina nova; as
    # zonas vao de duas em duas, com largura fixa para caberem as duas.
    folhas = "\n\n".join(
        f'<h4 style="page-break-before: always">{NOMES[pg]}</h4>\n'
        f'<p><img src="folhas/{pg}.jpg" alt="{NOMES[pg]}: caixas de cada OCR"></p>'
        for pg in ORDEM_IMAGENS)
    zonas = "\n\n".join(
        (f'<h4 style="page-break-before: always">{NOMES[pg]}</h4>\n' if i % 2 == 0 else f"<h4>{NOMES[pg]}</h4>\n")
        + f'<p><img src="zonas/{pg}.jpg" width="400" alt="{NOMES[pg]}: zonas do gabarito"></p>'
        for i, pg in enumerate(ORDEM_IMAGENS))
    texto = texto.replace("{{FOLHAS}}", folhas).replace("{{ZONAS}}", zonas)
    sobra = re.findall(r"\{\{[A-Z_]+\}\}", texto)
    if sobra:
        raise SystemExit(f"faltou preencher: {sobra}")
    MONTADO.write_text(texto, encoding="utf-8", newline="\n")
    print("montado:", MONTADO)


def gravar() -> None:
    raiz = PASTA.parents[1]
    sys.path.insert(0, str(raiz))
    import relatorio

    texto = MONTADO.read_text(encoding="utf-8")
    saida = relatorio.gravar(texto, PASTA / NOME, titulo="Item 1.3: comparação dos OCRs")
    for k, v in saida.items():
        print(k, v)


if __name__ == "__main__":
    {"montar": montar, "gravar": gravar}[sys.argv[1]]()
