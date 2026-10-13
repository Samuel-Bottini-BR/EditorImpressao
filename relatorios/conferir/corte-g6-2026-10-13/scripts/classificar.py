"""Separa as paginas do dados.json em melhorou / igual / piorou, comparando
a ordem nova (C) com a ordem antiga de mesmo angulo (B): a diferenca entre as
duas e SO a ordem do preparo. Guarda tambem a comparacao com o livro antigo
de verdade (A: ordem antiga + conta do programa).

A REGRA (numero so separa; quem julga e o olho, nas imagens lado a lado)
    Faixa escura na beirada (mascara "escuro": mais escuro que 60% do papel):
        piorou   se a faixa cresceu 0,5 ponto percentual da pagina ou mais
        melhorou se diminuiu 0,5 ponto ou mais
    Conteudo impresso (tinta que nao encosta na beirada da pagina inteira):
        piorou   se a tinta que fica de fora cresceu 0,1 ponto ou mais, ou se
                 as pecas partidas + de fora cresceram 2 ou mais
        melhorou no contrario
    Piorou num e melhorou no outro = "piorou" (com a nota do que melhorou).
    Angulo abaixo de 0,1 grau nas duas = a pagina nao e girada: as duas
    ordens dao a MESMA imagem ("identica").

Grava classificacao.json e escreve a tabela no terminal.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent
LIMITE_FAIXA = 0.005
LIMITE_TINTA = 0.001
LIMITE_PECAS = 2


def comparar(antiga: dict, nova: dict) -> dict:
    area_a = antiga["tamanho_px"][0] * antiga["tamanho_px"][1]
    area_n = nova["tamanho_px"][0] * nova["tamanho_px"][1]
    d_faixa = nova["beirada_escuro"] - antiga["beirada_escuro"]
    d_pb = (nova["beirada_pb"] or 0.0) - (antiga["beirada_pb"] or 0.0)
    d_tinta = nova["tinta_perdida"] - antiga["tinta_perdida"]
    d_pecas = (nova["pecas_partidas"] + nova["pecas_fora"]) - (antiga["pecas_partidas"] + antiga["pecas_fora"])
    lados = {k: round(nova["lados_escuro"][k]["mm"] - antiga["lados_escuro"][k]["mm"], 2)
             for k in ("esq", "dir", "topo", "pe")}
    piorou, melhorou = [], []
    if d_faixa >= LIMITE_FAIXA:
        piorou.append("faixa escura")
    elif d_faixa <= -LIMITE_FAIXA:
        melhorou.append("faixa escura")
    if d_tinta >= LIMITE_TINTA or d_pecas >= LIMITE_PECAS:
        piorou.append("conteudo cortado")
    elif d_tinta <= -LIMITE_TINTA or d_pecas <= -LIMITE_PECAS:
        melhorou.append("conteudo cortado")
    identica = (antiga["tamanho_px"] == nova["tamanho_px"] and abs(nova["angulo"]) < 0.1
                and abs(antiga["angulo"]) < 0.1 and antiga["recorte"] == nova["recorte"])
    classe = "piorou" if piorou else ("melhorou" if melhorou else "igual")
    return {"classe": classe, "piorou_em": piorou, "melhorou_em": melhorou, "identica": identica,
            "d_faixa_pp": round(100 * d_faixa, 2), "d_faixa_pb_pp": round(100 * d_pb, 2),
            "d_tinta_perdida_pp": round(100 * d_tinta, 3), "d_pecas": d_pecas,
            "d_area_pct": round(100 * (area_n / area_a - 1), 1), "d_faixa_mm_por_lado": lados,
            # nota so para ordenar "as que mais melhoraram / pioraram"
            "nota": round(-100 * d_faixa - 500 * d_tinta - 0.2 * d_pecas, 2)}


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    saida = {}
    for base, v in sorted(dados.items()):
        if "C" not in v:
            saida[base] = {"erro": v.get("erro")}
            continue
        saida[base] = {"no_gabarito": v.get("no_gabarito", False),
                       "so_a_ordem": comparar(v["B"], v["C"]),
                       "contra_o_livro_antigo": comparar(v["A"], v["C"])}
    (PASTA / "classificacao.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False),
                                              encoding="utf-8")
    for chave, titulo in (("so_a_ordem", "SO A ORDEM (B -> C)"),
                          ("contra_o_livro_antigo", "CONTRA O LIVRO ANTIGO (A -> C)")):
        print("\n" + titulo)
        for classe in ("piorou", "melhorou", "igual"):
            quais = [(b, s[chave]) for b, s in saida.items() if chave in s and s[chave]["classe"] == classe]
            identicas = sum(1 for _b, c in quais if c["identica"])
            print(f"  {classe}: {len(quais)}" + (f" (das quais {identicas} identicas, sem giro)" if classe == "igual" else ""))
            if classe == "igual":
                continue
            for b, c in sorted(quais, key=lambda t: t[1]["nota"]):
                print(f"     {b:32s} faixa {c['d_faixa_pp']:+6.2f} pp  pb {c['d_faixa_pb_pp']:+6.2f} pp  "
                      f"tinta fora {c['d_tinta_perdida_pp']:+6.3f} pp  pecas {c['d_pecas']:+3d}  "
                      f"area {c['d_area_pct']:+5.1f}%  {c['piorou_em']} {c['melhorou_em']}")
    erros = [b for b, s in saida.items() if "erro" in s]
    print("\ncom erro:", erros)
    return 0


if __name__ == "__main__":
    sys.exit(main())
