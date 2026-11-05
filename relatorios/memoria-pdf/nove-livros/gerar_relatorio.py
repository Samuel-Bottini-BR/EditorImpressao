"""Gera o relatório "memória nos 9 livros do acervo" nos três formatos (05/11/2026).

Lê as medidas de ../medidas-9-livros/medidas/ (medir_livro.py e comparar_pdfs.py)
e grava relatorio.md/.html/.pdf com relatorio.gravar (CLAUDE.md §2).
Uso: python relatorios/memoria-pdf/nove-livros/gerar_relatorio.py
Seguro mudar: o texto. Nada aqui mexe no programa.
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent
MEDIDAS = PASTA.parent / "medidas-9-livros" / "medidas"
sys.path.insert(0, str(PASTA.parents[2]))

import relatorio  # noqa: E402

LIVROS = [  # curto, nome que o Samuel conhece
    ("marial", "Marial de sermoens"),
    ("graduale", "Graduale - Saeculum XIV"),
    ("rhetorica", "Rhetorica Christiana"),
    ("escola", "Na escola de Jesus"),
    ("horas", "Livro de Horas - Luís XIV"),
    ("palatino", "Palatino"),
    ("siebmacher", "Siebmacher"),
    ("pesel", "Pesel (broderies anglaises)"),
    ("boecio", "Boécio"),
]


def _ler(nome: str) -> dict | None:
    f = MEDIDAS / f"{nome}.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def _mb(x) -> str:
    return "-" if x is None else f"{x:,.0f}".replace(",", ".")


def _tempo(seg: dict) -> str:
    total = (seg.get("analisar") or 0) + (seg.get("processar") or 0)
    m, s = divmod(round(total), 60)
    return f"{m} min {s:02d} s"


def _medianas(d: dict) -> list[int]:
    proc = [a for a in d["amostras"] if a[1] == "processar as páginas"]
    n = len(proc)
    return [round(statistics.median(a[3] for a in proc[i * n // 4:(i + 1) * n // 4])) for i in range(4)]


def tabela() -> tuple[list[str], list[str], dict]:
    linhas = ["| Livro | Folhas | Pico do programa | PDF | Tempo | Terminou? | Igual ao antigo? |",
              "|---|---|---|---|---|---|---|"]
    detalhe = ["| Livro | Pico no 1º quarto | no 4º quarto | Memória \"de base\" no 1º quarto | no 4º quarto | Páginas: esperadas / no PDF |",
               "|---|---|---|---|---|---|"]
    resumo = {}
    for curto, nome in LIVROS:
        d = _ler(f"{curto}-novo")
        if d is None:
            linhas.append(f"| {nome} | - | - | - | - | não medido | - |")
            continue
        comp = _ler(f"{curto}-comparacao")
        if comp is None:
            igual = "não comparado"
        else:
            amostra = len(comp["amostra"])
            igual = (f"sim ({comp['paginas_novo']} páginas; {amostra} páginas pixel a pixel)"
                     if comp["tudo_igual"] else "**NÃO**")
        folhas = f"{d['folhas']}" + (f" de {d['folhas_do_livro_inteiro']} (pedaço)"
                                     if d["folhas"] != d["folhas_do_livro_inteiro"] else "")
        terminou = "sim" if d["erro"] is None and d["paginas_no_pdf"] == d["paginas_esperadas"] else f"**não** ({d['erro']})"
        pdf = f"{d['pdf_mb'] / 1024:.1f} GB".replace(".", ",") if d["pdf_mb"] and d["pdf_mb"] >= 1024 else f"{_mb(d['pdf_mb'])} MB"
        linhas.append(f"| {nome} | {folhas} | {_mb(d['pico_total']['privado_mb'])} MB | {pdf} | "
                      f"{_tempo(d['segundos'])} | {terminou} | {igual} |")
        q = d["pico_por_quarto_do_livro"]
        med = _medianas(d)
        detalhe.append(f"| {nome} | {_mb(q['1o_quarto']['privado_mb'])} MB | {_mb(q['4o_quarto']['privado_mb'])} MB | "
                       f"{_mb(med[0])} MB | {_mb(med[3])} MB | {d['paginas_esperadas']} / {d['paginas_no_pdf']} |")
        resumo[curto] = {"pdf": d["pdf_mb"], "subida_base": med[3] - med[0]}
    return linhas, detalhe, resumo


def tabela_antigo() -> list[str]:
    linhas = ["| Livro | PDF | Pico antigo | Pico novo | Base antiga 1º → 4º quarto | Base nova 1º → 4º quarto |",
              "|---|---|---|---|---|---|"]
    for curto, nome in LIVROS:
        a, n = _ler(f"{curto}-antigo"), _ler(f"{curto}-novo")
        if a is None or n is None:
            continue
        ma, mn = _medianas(a), _medianas(n)
        linhas.append(f"| {nome} | {_mb(a['pdf_mb'])} MB | {_mb(a['pico_total']['privado_mb'])} MB | "
                      f"{_mb(n['pico_total']['privado_mb'])} MB | {_mb(ma[0])} → {_mb(ma[3])} MB (+{ma[3] - ma[0]}) | "
                      f"{_mb(mn[0])} → {_mb(mn[3])} MB (+{mn[3] - mn[0]}) |")
    return linhas


def main() -> int:
    linhas, detalhe, _ = tabela()
    texto = (PASTA / "texto.md").read_text(encoding="utf-8")
    texto = (texto.replace("{tabela}", "\n".join(linhas))
                  .replace("{detalhe}", "\n".join(detalhe))
                  .replace("{antigo}", "\n".join(tabela_antigo())))
    feitos = relatorio.gravar(texto, PASTA / "relatorio", titulo="Memória nos 9 livros do acervo")
    for tipo, caminho in feitos.items():
        print(tipo, caminho)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
