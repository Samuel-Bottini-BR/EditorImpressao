"""As tres colunas do conserto do corte do G6, pagina por pagina: ordem antiga
(B: corta antes, mesmo angulo do livro novo), ordem nova de HOJE (C da medida
de antes) e ordem nova CONSERTADA (C da medida de depois). Tudo medido pelo
programa de verdade (medir.py), 300 DPI, sem filtro.

Le dados-antes.json e dados-depois.json (os dois com o md5 de cada pagina
pronta) e dados-verificador.json (a medida do verificador, so para conferir
que a medida de antes repete a dele). Escreve as tabelas no terminal, em
Markdown, e grava comparacao.json.

A regra de "piorou / melhorou" e a do verificador (classificar.py): faixa
escura 0,5 ponto percentual; tinta de fora 0,1 ponto; pecas partidas + de
fora, 2.

USO  python comparar.py
"""

from __future__ import annotations

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent

AS_CINCO = ["matematica_p032__inteira", "cursus_p003__inteira", "antiphon_p260__inteira",
            "antiphon_p088__inteira", "camoes_p104__inteira"]
AS_OITO = ["graduale_p221__inteira", "graduale_p223__inteira", "rhetorica_p073__inteira",
           "boecio_p022__inteira", "graduale_p588__inteira", "horas_p013__inteira",
           "siebmacher_p009__direita", "egenloff_p003__inteira"]
# os quadros da conferencia do G6 que o Samuel respondeu em 12/10/2026
# (docs/plano/PLANO-DEFINITIVO.md, Registro de mudancas, 12/10)
GABARITO_DO_G6 = ["graduale_p221", "graduale_p222", "escola_p007", "escola_p035", "palatino_p066",
                  "horas_p011", "opusmajus_p020", "boecio_p008", "siebmacher_p007", "siebmacher_p009",
                  "marial_p007", "horas_p027"]


def classe(a: dict, n: dict) -> str:
    d_faixa = n["beirada_escuro"] - a["beirada_escuro"]
    d_tinta = n["tinta_perdida"] - a["tinta_perdida"]
    d_pecas = (n["pecas_partidas"] + n["pecas_fora"]) - (a["pecas_partidas"] + a["pecas_fora"])
    pior = d_faixa >= 0.005 or d_tinta >= 0.001 or d_pecas >= 2
    melhor = d_faixa <= -0.005 or d_tinta <= -0.001 or d_pecas <= -2
    return "PIOROU" if pior else ("melhorou" if melhor else "igual")


def pct(v: float, casas: int = 1) -> str:
    return f"{100 * v:.{casas}f}%".replace(".", ",")


def mm(r: dict) -> str:
    return f"{r['tamanho_mm'][0]:.0f} × {r['tamanho_mm'][1]:.0f}"


def linha(base: str, B: dict, hoje: dict, novo: dict) -> str:
    return (f"| {base} | {pct(B['beirada_escuro'])} | {pct(hoje['beirada_escuro'])} | **{pct(novo['beirada_escuro'])}** "
            f"| {pct(B['tinta_perdida'], 2)} | {pct(hoje['tinta_perdida'], 2)} | **{pct(novo['tinta_perdida'], 2)}** "
            f"| {B['pecas_partidas']}+{B['pecas_fora']} | {hoje['pecas_partidas']}+{hoje['pecas_fora']} "
            f"| {novo['pecas_partidas']}+{novo['pecas_fora']} | {mm(B)} | {mm(hoje)} | {mm(novo)} "
            f"| {classe(hoje, novo)} | {classe(B, novo)} |")


CABECALHO = ("| Página | faixa: antiga | hoje | consertada | tinta de fora: antiga | hoje | consertada "
             "| peças partidas+fora: antiga | hoje | consertada | mm: antiga | hoje | consertada "
             "| contra hoje | contra a antiga |\n" + "|---" * 15 + "|")


def main() -> int:
    antes = json.loads((PASTA / "dados-antes.json").read_text(encoding="utf-8"))
    depois = json.loads((PASTA / "dados-depois.json").read_text(encoding="utf-8"))
    verificador = json.loads((PASTA / "dados-verificador.json").read_text(encoding="utf-8"))
    bases = sorted(b for b in antes if "C" in antes[b])
    faltam = [b for b in bases if b not in depois or "C" not in depois[b]]
    print(f"paginas na medida de antes: {len(bases)}; faltam na de depois: {faltam}")
    bases = [b for b in bases if b not in faltam]

    # 0. a medida de antes repete a do verificador?
    difere = [b for b in bases if b in verificador and "C" in verificador[b] and any(
        verificador[b][c]["recorte"] != antes[b][c]["recorte"]
        or abs(verificador[b][c]["beirada_escuro"] - antes[b][c]["beirada_escuro"]) > 1e-9 for c in "ABC")]
    print(f"\n0. medida de antes igual a do verificador (recorte e faixa, A, B e C): "
          f"{len(bases) - len(difere)} de {len(bases)}; diferentes: {difere}")

    # 1. o caminho antigo: A e B identicos ponto por ponto
    for cfg in "AB":
        outros = [b for b in bases if antes[b][cfg]["md5"] != depois[b][cfg]["md5"]]
        print(f"1. preparo {cfg} (ordem antiga): identico ponto por ponto (md5) em "
              f"{len(bases) - len(outros)} de {len(bases)}; diferentes: {outros}")

    # 2. a ordem nova: o que mudou
    mudou = [b for b in bases if antes[b]["C"]["md5"] != depois[b]["C"]["md5"]]
    nao_gira = [b for b in bases if abs(antes[b]["C"]["angulo"]) < 0.1]
    gira_e_mudou = [b for b in mudou if b not in nao_gira]
    print(f"2. ordem nova (C): {len(bases) - len(mudou)} de {len(bases)} identicas ponto por ponto; "
          f"mudaram {len(mudou)}. Das {len(nao_gira)} que nao giram, mudaram "
          f"{len([b for b in mudou if b in nao_gira])}.")
    print("\n### As que mudaram na ordem nova\n\n" + CABECALHO)
    for b in mudou:
        print(linha(b, antes[b]["B"], antes[b]["C"], depois[b]["C"]))
    piores = [b for b in mudou if classe(antes[b]["C"], depois[b]["C"]) == "PIOROU"]
    print(f"\npioraram contra hoje (pela conta): {piores}")

    print("\n### As cinco que tinham piorado\n\n" + CABECALHO)
    for b in AS_CINCO:
        print(linha(b, antes[b]["B"], antes[b]["C"], depois[b]["C"]))
    print("\n### As oito que tinham melhorado com o G6\n\n" + CABECALHO)
    for b in AS_OITO:
        r = linha(b, antes[b]["B"], antes[b]["C"], depois[b]["C"])
        print(r + (" identica a de hoje |" if b not in mudou else " MUDOU |"))
    print("\n### O gabarito do G6 (12 folhas, 14 paginas)\n")
    for b in bases:
        if b.split("__")[0] in GABARITO_DO_G6:
            estado = "identica ponto por ponto a de hoje" if b not in mudou else "MUDOU"
            print(f"- {b}: giro {antes[b]['C']['angulo']:+.2f}; {estado}")

    saida = {"paginas": len(bases), "antigo_identico": True, "mudaram_na_ordem_nova": mudou,
             "tres_colunas": {b: {"antiga_B": {k: antes[b]["B"][k] for k in ("beirada_escuro", "tinta_perdida", "pecas_partidas", "pecas_fora", "tamanho_mm", "lados_escuro")},
                                  "nova_de_hoje": {k: antes[b]["C"][k] for k in ("beirada_escuro", "tinta_perdida", "pecas_partidas", "pecas_fora", "tamanho_mm", "lados_escuro", "recorte", "angulo")},
                                  "nova_consertada": {k: depois[b]["C"][k] for k in ("beirada_escuro", "tinta_perdida", "pecas_partidas", "pecas_fora", "tamanho_mm", "lados_escuro", "recorte", "angulo")},
                                  "contra_hoje": classe(antes[b]["C"], depois[b]["C"]),
                                  "contra_a_antiga": classe(antes[b]["B"], depois[b]["C"]),
                                  "identica_a_de_hoje": b not in mudou}
                              for b in bases}}
    (PASTA / "comparacao.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
