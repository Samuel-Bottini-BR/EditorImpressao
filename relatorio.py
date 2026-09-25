"""Grava todo relatorio em duas versoes: uma para o Samuel, outra para mim.

O Samuel nao abre .md - o Acrobat recusa o arquivo e nao ha o que fazer. Um
relatorio que a pessoa nao consegue abrir nao e relatorio.

Entao todo relatorio sai em dois arquivos com o mesmo nome:

    relatorio.md     texto puro, que eu leio e o git compara linha a linha
    relatorio.html   formatado, que abre com dois cliques no navegador

O HTML nao depende de internet nem de programa instalado: o estilo vai dentro
do proprio arquivo. E as imagens que estiverem ao lado dele aparecem embutidas,
para o relatorio poder ser lido sozinho, sem abrir pasta.
"""

from __future__ import annotations

import html as _html
import re
from datetime import datetime
from pathlib import Path

ESTILO = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  font: 17px/1.65 "Segoe UI", system-ui, sans-serif;
  max-width: 46rem; margin: 0 auto; padding: 2.5rem 1.5rem 6rem;
  color: #1c1c1e; background: #fdfdfc;
}
h1 { font-size: 2rem; line-height: 1.2; margin: 0 0 .3em; letter-spacing: -.02em; }
h2 { font-size: 1.35rem; margin: 2.4em 0 .6em; padding-top: .8em;
     border-top: 1px solid #e6e4e0; letter-spacing: -.01em; }
h3 { font-size: 1.1rem; margin: 1.8em 0 .4em; }
h1 + p, h2 + p { margin-top: .4em; }
p, li { margin: 0 0 .9em; }
ul, ol { padding-left: 1.3em; }
strong { font-weight: 640; }
code {
  font: .88em ui-monospace, "Cascadia Code", Consolas, monospace;
  background: #f1efec; padding: .12em .35em; border-radius: 4px;
}
pre {
  background: #f1efec; padding: 1em 1.1em; border-radius: 8px;
  overflow-x: auto; line-height: 1.5;
}
pre code { background: none; padding: 0; }
blockquote {
  margin: 1.2em 0; padding: .1em 0 .1em 1.1em;
  border-left: 3px solid #c9c5be; color: #55524d;
}
table {
  border-collapse: collapse; width: 100%; margin: 1.2em 0;
  font-size: .95rem; display: block; overflow-x: auto;
}
th, td { padding: .5em .8em; text-align: left; border-bottom: 1px solid #e6e4e0; }
th { font-weight: 620; background: #f7f5f2; white-space: nowrap; }
tr:last-child td { border-bottom: none; }
img { max-width: 100%; height: auto; border-radius: 6px; margin: 1em 0;
      border: 1px solid #e6e4e0; }
hr { border: none; border-top: 1px solid #e6e4e0; margin: 2.5em 0; }
.rodape { margin-top: 4em; padding-top: 1.2em; border-top: 1px solid #e6e4e0;
          font-size: .85rem; color: #86827c; }
@media (prefers-color-scheme: dark) {
  body { color: #e8e6e3; background: #1a1917; }
  h2 { border-top-color: #35332f; }
  code, pre, th { background: #262421; }
  th, td { border-bottom-color: #35332f; }
  blockquote { border-left-color: #4a4741; color: #b0aca6; }
  img { border-color: #35332f; }
  .rodape { border-top-color: #35332f; color: #7d7973; }
}
@media print {
  body { max-width: none; padding: 0; color: #000; background: #fff; }
  h2 { page-break-after: avoid; }
  table, img { page-break-inside: avoid; }
}
"""


def _markdown_para_html(texto: str) -> str:
    """Converte com a biblioteca markdown; se faltar, faz o basico na mao."""
    try:
        import markdown

        return markdown.markdown(
            texto, extensions=["tables", "fenced_code", "sane_lists"]
        )
    except Exception:  # noqa: BLE001 - sem a biblioteca o relatorio ainda sai
        return _conversao_simples(texto)


def _conversao_simples(texto: str) -> str:
    """Plano B sem dependencia: titulos, tabelas, listas, negrito e codigo."""
    saida: list[str] = []
    linhas = texto.split("\n")
    i = 0
    while i < len(linhas):
        linha = linhas[i]

        if linha.startswith("|") and i + 1 < len(linhas) and set(
                linhas[i + 1].replace("|", "").strip()) <= set("-: "):
            cabecalho = [c.strip() for c in linha.strip("|").split("|")]
            saida.append("<table><thead><tr>"
                         + "".join(f"<th>{_inline(c)}</th>" for c in cabecalho)
                         + "</tr></thead><tbody>")
            i += 2
            while i < len(linhas) and linhas[i].startswith("|"):
                celulas = [c.strip() for c in linhas[i].strip("|").split("|")]
                saida.append("<tr>" + "".join(f"<td>{_inline(c)}</td>"
                                              for c in celulas) + "</tr>")
                i += 1
            saida.append("</tbody></table>")
            continue

        if linha.startswith("#"):
            nivel = len(linha) - len(linha.lstrip("#"))
            saida.append(f"<h{nivel}>{_inline(linha.lstrip('# '))}</h{nivel}>")
        elif linha.startswith("> "):
            saida.append(f"<blockquote><p>{_inline(linha[2:])}</p></blockquote>")
        elif linha.strip().startswith(("- ", "* ")):
            saida.append("<ul>")
            while i < len(linhas) and linhas[i].strip().startswith(("- ", "* ")):
                saida.append(f"<li>{_inline(linhas[i].strip()[2:])}</li>")
                i += 1
            saida.append("</ul>")
            continue
        elif linha.strip():
            saida.append(f"<p>{_inline(linha)}</p>")
        i += 1
    return "\n".join(saida)


def _inline(texto: str) -> str:
    """Formatacao dentro de uma linha: escapa HTML e converte `codigo`,
    **negrito** e *italico*. Usado pelo conversor simples (sem a lib markdown)."""
    t = _html.escape(texto)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", t)
    return t


def _titulo_de(texto: str, padrao: str) -> str:
    """O titulo do relatorio e o primeiro `# ...` do markdown, ou `padrao` se nao houver."""
    for linha in texto.split("\n"):
        if linha.startswith("# "):
            return linha[2:].strip()
    return padrao


def montar_html(texto_markdown: str, titulo: str | None = None) -> str:
    """Pagina completa, com o estilo dentro e sem depender de nada externo."""
    titulo = titulo or _titulo_de(texto_markdown, "Relatório")
    corpo = _markdown_para_html(texto_markdown)
    quando = datetime.now().strftime("%d/%m/%Y às %H:%M")
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{_html.escape(titulo)}</title>
<style>{ESTILO}</style>
</head>
<body>
{corpo}
<p class="rodape">Editor de Impressão &middot; gerado em {quando}</p>
</body>
</html>
"""


# Teto de paginas de um relatorio. Existe por seguranca, nao por limite de
# tamanho: o maior relatorio do projeto tem cinco paginas. Ver _paginar.
PAGINAS_MAXIMAS = 200


def _paginar(html: str, caminho: Path) -> tuple[int, bool]:
    """Escreve o HTML em paginas A4. Devolve (quantas paginas, terminou).

    O laco PRECISA de teto. O Story do PyMuPDF devolve "ainda tem mais" sem
    consumir nada quando um elemento nao cabe na area util, e ai o programa
    escreve paginas para sempre: medido, a linha de base de 04/08/2026 entrava
    num ciclo de tres paginas que se repetia sem fim, com o conteudo repetido, e
    deixava um .pdf de zero byte. Travar e pior que falhar - ninguem sabe se
    esperar ou matar o programa.
    """
    import fitz

    story = fitz.Story(html=html)
    escritor = fitz.DocumentWriter(str(caminho))
    moldura = fitz.paper_rect("a4")
    area = moldura + (50, 50, -50, -50)
    mais, paginas = True, 0
    while mais and paginas < PAGINAS_MAXIMAS:
        paginas += 1
        dispositivo = escritor.begin_page(moldura)
        mais, _ = story.place(area)
        story.draw(dispositivo)
        escritor.end_page()
    escritor.close()
    return paginas, not mais


def _pagina_simples(corpo: str, quando: str) -> str:
    """O mesmo relatorio num estilo que o Story sempre consegue paginar.

    Sem margens, sem bordas e sem entrelinha: e a combinacao dessas com uma
    tabela longa que faz o layout entrar em ciclo. Medido no relatorio que
    travava, este estilo fecha em quatro paginas.
    """
    return (
        "<html><head><style>"
        "body { font-family: sans-serif; font-size: 10pt; color: #1c1c1e; }"
        "table { border-collapse: collapse; width: 100%; font-size: 9pt; }"
        "th, td { padding: 3pt 5pt; text-align: left; }"
        "</style></head><body>" + corpo +
        "<p>Editor de Impressão &middot; gerado em " + quando + "</p>"
        "</body></html>"
    )


def gravar_pdf(texto_markdown: str, destino: str | Path,
               titulo: str | None = None) -> Path | None:
    """Gera o PDF do relatorio. Devolve None se nao for possivel.

    Usa o proprio PyMuPDF, que ja e dependencia do programa - nada de motor de
    navegador nem de instalador extra.
    """
    import fitz

    caminho = Path(destino).with_suffix(".pdf")
    corpo = _markdown_para_html(texto_markdown)
    quando = datetime.now().strftime("%d/%m/%Y às %H:%M")

    # O Story do PyMuPDF entende um subconjunto de CSS; o estilo aqui e mais
    # simples que o do HTML de propósito.
    pagina_html = f"""<html><head><style>
    body {{ font-family: sans-serif; font-size: 10pt; line-height: 1.5; color: #1c1c1e; }}
    h1 {{ font-size: 19pt; margin: 0 0 8pt; }}
    h2 {{ font-size: 13pt; margin: 16pt 0 5pt; color: #33312e; }}
    h3 {{ font-size: 11pt; margin: 12pt 0 4pt; }}
    p, li {{ margin: 0 0 6pt; }}
    table {{ border-collapse: collapse; width: 100%; margin: 8pt 0; font-size: 9pt; }}
    th, td {{ padding: 3pt 5pt; text-align: left; border-bottom: 1px solid #ddd; }}
    th {{ background: #f2f0ed; font-weight: bold; }}
    code {{ font-family: monospace; font-size: 9pt; background: #f2f0ed; }}
    blockquote {{ margin: 8pt 0 8pt 12pt; color: #55524d; }}
    .rodape {{ margin-top: 20pt; font-size: 8pt; color: #86827c; }}
    </style></head><body>{corpo}
    <p class="rodape">Editor de Impressão &middot; gerado em {quando}</p>
    </body></html>"""

    try:
        paginas, terminou = _paginar(pagina_html, caminho)
        if not terminou:
            # O layout entrou em ciclo: ver _paginar. O mesmo texto num estilo
            # sem margens nem bordas fecha normalmente, entao vale a pena
            # regravar assim - relatorio simples e melhor que relatorio nenhum.
            paginas, terminou = _paginar(
                _pagina_simples(corpo, quando), caminho)
        return caminho
    except Exception:  # noqa: BLE001 - sem PDF o md e o html ainda saem
        return None


def gravar(texto_markdown: str, destino: str | Path,
           titulo: str | None = None) -> dict[str, Path]:
    """Grava o relatorio nas tres versoes.

    Devolve um dicionario com as chaves md, html e pdf (esta ultima ausente se
    a geracao falhar). destino pode vir com extensao ou sem.
    """
    base = Path(destino).with_suffix("")
    base.parent.mkdir(parents=True, exist_ok=True)

    md = base.with_suffix(".md")
    md.write_text(texto_markdown, encoding="utf-8")

    htm = base.with_suffix(".html")
    htm.write_text(montar_html(texto_markdown, titulo), encoding="utf-8")

    saida = {"md": md, "html": htm}
    pdf = gravar_pdf(texto_markdown, base, titulo)
    if pdf is not None:
        saida["pdf"] = pdf
    return saida


def converter_pasta(pasta: str | Path, recursivo: bool = True) -> list[Path]:
    """Gera html e pdf de todo .md que ainda nao tem par. Devolve os criados."""
    pasta = Path(pasta)
    padrao = "**/*.md" if recursivo else "*.md"
    criados: list[Path] = []
    for md in sorted(pasta.glob(padrao)):
        texto = md.read_text(encoding="utf-8")
        for extensao, faz in ((".html", lambda: md.with_suffix(".html").write_text(
                montar_html(texto), encoding="utf-8")),
                (".pdf", lambda: gravar_pdf(texto, md))):
            par = md.with_suffix(extensao)
            if par.exists() and par.stat().st_mtime >= md.stat().st_mtime:
                continue
            faz()
            if par.exists():
                criados.append(par)
    return criados


# Uma pasta por filtro. O nome que aparece na Area de Trabalho fica em
# maiuscula para separar do nome dos testes, que vao dentro.
PASTAS_DE_FILTRO = {
    "magico pro": "MAGICO PRO",
    "preto e branco": "PRETO E BRANCO",
    "melhorar": "MELHORAR",
    "selecao": "SELECAO DE REGIOES",
    "recorte": "RECORTE DE BORDAS",
    "dividir": "DIVIDIR PAGINAS",
    "cadernos": "CADERNOS",
    "desempenho": "DESEMPENHO",
    "robustez": "ROBUSTEZ",
}


def pasta_de_teste(assunto: str, filtro: str = "", raiz: str | Path | None = None) -> Path:
    """Cria a pasta de um teste novo, no padrao combinado com o Samuel.

        TESTES EDITOR DE IMPRESSAO\\
            MAGICO PRO\\
                2026-08-01 14h30 - contraste local no papel
            PRETO E BRANCO\\
                2026-07-30 22h52 - comparacao dos 18 binarizadores
                2026-07-31 07h25 - rubricacao vermelha preservada

    O filtro e uma PASTA de verdade, e nao um pedaco do nome: assim tudo do
    Magico pro fica junto e da para percorrer a historia de um filtro so.
    Dentro dela, data e hora no comeco ordenam sozinho e deixam comparar duas
    rodadas do mesmo dia.
    """
    raiz = Path(raiz or r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO")
    chave = (filtro or "").strip().lower()
    pasta_filtro = PASTAS_DE_FILTRO.get(chave, chave.upper() or "OUTROS")

    carimbo = datetime.now().strftime("%Y-%m-%d %Hh%M")
    pasta = raiz / pasta_filtro / f"{carimbo} - {_nome_de_pasta(assunto)}"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


# Caracteres que o Windows nao aceita em nome de pasta.
PROIBIDOS_NO_NOME = '<>:"/\\|?*'


def _nome_de_pasta(assunto: str) -> str:
    """Deixa o assunto virar nome de pasta sem derrubar o teste.

    Um assunto com dois pontos - "letra arredondada: raio da nitidez" - fazia o
    mkdir estourar no meio de uma bateria, depois de todo o trabalho pesado ja
    feito. O assunto e texto escrito a mao a cada teste, entao a pontuacao vai
    aparecer.
    """
    limpo = "".join(" " if c in PROIBIDOS_NO_NOME else c for c in assunto)
    limpo = " ".join(limpo.split()).strip(" .")
    return limpo or "sem assunto"


if __name__ == "__main__":
    import sys

    alvos = sys.argv[1:] or [
        str(Path(__file__).resolve().parent / "relatorios"),
        r"D:\programas\EditorImpressao-arquivos\TESTES EDITOR DE IMPRESSAO",
    ]
    for alvo in alvos:
        caminho = Path(alvo)
        if caminho.is_dir():
            feitos = converter_pasta(caminho)
            print(f"{caminho}: {len(feitos)} arquivo(s) gerado(s)")
            for f in feitos:
                print(f"   {f.name}")
        elif caminho.suffix == ".md" and caminho.exists():
            _, htm = gravar(caminho.read_text(encoding="utf-8"), caminho)
            print(f"   {htm}")
