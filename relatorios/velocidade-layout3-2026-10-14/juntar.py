"""Junta as rodadas da medicao de velocidade do layout juntado (14/10/2026) em tabelas.

So le os .json que o teste_velocidade.py gravou em rodadas/<nome>/ e a
anotacao.json de cada rodada (hora, memoria livre, uso do processador), e
imprime as tabelas em markdown. Nao mede nada e nao grava nada.

Uso: python juntar.py   (de qualquer pasta)
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RODADAS = AQUI / "rodadas"
ORDEM = ["antes-1", "depois-1", "antes-2", "depois-2", "antes-3", "depois-3"]

# (chave no resumo do .json, nome, divisor para "por unidade", nome da unidade)
MEDIDAS = [
    ("abrir_total_s", "Abrir o livro (300 folhas)", 300, "por folha"),
    ("troca_media_s", "Trocar de pagina (media de 20)", 1, ""),
    ("troca_pior_s", "Trocar de pagina (a pior das 20)", 1, ""),
    ("processar_magico_pro_s", "Processar 10 paginas em Magico pro", 10, "por pagina"),
    ("processar_preto_e_branco_s", "Processar 10 paginas em Preto e branco", 10, "por pagina"),
]


def n(valor: float, casas: int = 1) -> str:
    return f"{valor:.{casas}f}".replace(".", ",")


def ler(nome: str) -> dict | None:
    pasta = RODADAS / nome
    arquivos = sorted(pasta.glob("velocidade-*.json"))
    if not arquivos:
        return None
    dados = json.loads(arquivos[0].read_text(encoding="utf-8"))
    anotacao = json.loads((pasta / "anotacao.json").read_text(encoding="utf-8-sig"))
    return {"nome": nome, "braco": nome.split("-")[0], "dados": dados, "anotacao": anotacao}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rodadas = [r for r in (ler(nome) for nome in ORDEM) if r]
    if not rodadas:
        print("Nenhuma rodada pronta.")
        return 1

    print("## Todas as rodadas (mediana das 3 repeticoes de cada execucao)\n")
    print("| Rodada | Hora | Mem. livre antes | Processador antes | Abrir o livro | Troca (media) | "
          "Troca (pior) | Magico pro, 10 pag. | Preto e branco, 10 pag. | Memoria maxima | Durou |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rodadas:
        a, resumo = r["anotacao"], r["dados"]["resumo"]
        celulas = [n(resumo[chave]["mediana"], 2 if "troca" in chave else 1) + " s"
                   for chave, *_ in MEDIDAS]
        print(f"| {r['nome']} | {a['inicio'][11:16]} | {n(a['memoria_livre_antes_gb'], 2)} GB | "
              f"{a['processador_antes_pct']}% | " + " | ".join(celulas)
              + f" | {n(r['dados']['memoria']['pico_mb'], 0)} MB | {n(a['minutos'], 1)} min |")

    print("\n## Cada repeticao (3 por execucao)\n")
    print("| Rodada | Medida | 1a | 2a | 3a |")
    print("|---|---|---|---|---|")
    for r in rodadas:
        for chave, nome, *_ in MEDIDAS:
            valores = r["dados"]["resumo"][chave]["rodadas"]
            casas = 2 if "troca" in chave else 1
            print(f"| {r['nome']} | {nome} | " + " | ".join(n(v, casas) + " s" for v in valores) + " |")

    print("\n## Antes contra depois\n")
    print("| Medida | Antes (media das medianas) | Depois (media das medianas) | Diferenca | Em % | "
          "Por unidade | Vai-e-vem do antes | Vai-e-vem do depois | Pares (depois - antes) | "
          "Todas as 9: antes | Todas as 9: depois |")
    print("|---|---|---|---|---|---|---|---|---|---|---|")
    for chave, nome, divisor, unidade in MEDIDAS:
        casas = 2 if "troca" in chave else 1
        medianas = {"antes": [], "depois": []}
        todas = {"antes": [], "depois": []}
        for r in rodadas:
            medianas[r["braco"]].append(r["dados"]["resumo"][chave]["mediana"])
            todas[r["braco"]].extend(r["dados"]["resumo"][chave]["rodadas"])
        if not medianas["antes"] or not medianas["depois"]:
            continue
        ma, md = statistics.fmean(medianas["antes"]), statistics.fmean(medianas["depois"])
        dif = md - ma
        pares = [d - a for a, d in zip(medianas["antes"], medianas["depois"])]
        por = f"{dif / divisor * 1000:+.0f} ms {unidade}".replace(".", ",") if divisor > 1 else "-"

        def faixa(valores: list[float]) -> str:
            return (f"{n(min(valores), casas)} a {n(max(valores), casas)} s "
                    f"(abre {n(max(valores) - min(valores), casas)} s)")

        def resumo9(valores: list[float]) -> str:
            return (f"mediana {n(statistics.median(valores), casas)} s, "
                    f"de {n(min(valores), casas)} a {n(max(valores), casas)} s")

        print(f"| {nome} | {n(ma, casas)} s | {n(md, casas)} s | {dif:+.{casas}f} s".replace(".", ",")
              + f" | {dif / ma * 100:+.1f}%".replace(".", ",")
              + f" | {por} | {faixa(medianas['antes'])} | {faixa(medianas['depois'])} | "
              + "; ".join(f"{p:+.{casas}f}".replace(".", ",") for p in pares) + " s | "
              + f"{resumo9(todas['antes'])} | {resumo9(todas['depois'])} |")

    print("\n## Conferencias\n")
    for r in rodadas:
        d, a = r["dados"], r["anotacao"]
        print(f"- {r['nome']}: commit {a['commit']}, saida {a['codigo_de_saida']}, "
              f"livro {d['livro']['arquivo']} ({d['livro']['folhas']} folhas, {d['livro']['paginas']} paginas), "
              f"detector {'carregado' if d['preparo']['detector_de_regioes'] else 'NAO CARREGOU'}, "
              f"energia: {d['maquina']['energia']['texto']}, "
              f"mem. livre depois {n(a['memoria_livre_depois_gb'], 2)} GB, "
              f"trocas {len(d['configuracao']['lista_trocas'])}, "
              f"processadas {d['configuracao']['lista_processadas'][0] + 1} a "
              f"{d['configuracao']['lista_processadas'][-1] + 1}, "
              f"PDF Magico pro {n(d['rodadas'][0]['processar']['magico_pro']['tamanho_saida_mb'], 1)} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
