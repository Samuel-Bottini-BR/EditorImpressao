"""Junta as rodadas da medicao de velocidade do conserto do corte (13/10/2026).

So le os .json que o teste_velocidade.py gravou em rodadas/<nome>/ e a
anotacao.json de cada rodada, grava velocidade.json (os numeros que o
relatorio usa) e imprime as tabelas. Mesmo jeito do juntar.py da medicao do
G6 (relatorios/velocidade-g6-2026-10-12), com 2 rodadas de cada.

Uso: python juntar.py
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RODADAS = AQUI / "rodadas"
ORDEM = ["antes-1", "depois-1", "antes-2", "depois-2", "antes-3", "depois-3"]
MEDIDAS = [
    ("abrir_total_s", "Abrir o livro (300 folhas)", 300, "por folha"),
    ("troca_media_s", "Trocar de página (média de 20)", 1, ""),
    ("troca_pior_s", "Trocar de página (a pior das 20)", 1, ""),
    ("processar_magico_pro_s", "Processar 10 páginas em Mágico pro", 10, "por página"),
    ("processar_preto_e_branco_s", "Processar 10 páginas em Preto e branco", 10, "por página"),
]


def ler(nome: str) -> dict | None:
    pasta = RODADAS / nome
    arquivos = sorted(pasta.glob("velocidade-*.json"))
    if not arquivos or not (pasta / "anotacao.json").exists():
        return None
    return {"nome": nome, "braco": nome.split("-")[0],
            "dados": json.loads(arquivos[0].read_text(encoding="utf-8")),
            "anotacao": json.loads((pasta / "anotacao.json").read_text(encoding="utf-8-sig"))}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    rodadas = [r for r in (ler(nome) for nome in ORDEM) if r]
    if not rodadas:
        print("Nenhuma rodada pronta.")
        return 1
    saida = {"rodadas": [], "medidas": []}
    for r in rodadas:
        a, d = r["anotacao"], r["dados"]
        linha = {"nome": r["nome"], "braco": r["braco"], "commit": a["commit"], "hora": a["inicio"][11:16],
                 "minutos": a["minutos"], "memoria_livre_antes_gb": a["memoria_livre_antes_gb"],
                 "processador_antes_pct": a["processador_antes_pct"],
                 "outros_python_antes": a.get("outros_python_antes"),
                 "outros_python_depois": a.get("outros_python_depois"),
                 "codigo_de_saida": a["codigo_de_saida"], "arquivos_mexidos": a["arquivos_mexidos"],
                 "memoria_maxima_mb": d["memoria"]["pico_mb"],
                 "livro": d["livro"]["arquivo"], "folhas": d["livro"]["folhas"],
                 "detector": bool(d["preparo"]["detector_de_regioes"]),
                 "energia": d["maquina"]["energia"]["texto"],
                 "pdf_magico_pro_mb": d["rodadas"][0]["processar"]["magico_pro"]["tamanho_saida_mb"]}
        for chave, *_ in MEDIDAS:
            linha[chave] = {"mediana": d["resumo"][chave]["mediana"], "repeticoes": d["resumo"][chave]["rodadas"]}
        saida["rodadas"].append(linha)
        print(r["nome"], a["inicio"][11:16], f"{a['processador_antes_pct']}% proc",
              f"{a['memoria_livre_antes_gb']} GB", f"outros python {a.get('outros_python_antes')}",
              {c: d["resumo"][c]["mediana"] for c, *_ in MEDIDAS}, f"{a['minutos']} min", flush=True)
    for chave, nome, divisor, unidade in MEDIDAS:
        med = {"antes": [], "depois": []}
        todas = {"antes": [], "depois": []}
        for r in rodadas:
            med[r["braco"]].append(r["dados"]["resumo"][chave]["mediana"])
            todas[r["braco"]].extend(r["dados"]["resumo"][chave]["rodadas"])
        if not med["antes"] or not med["depois"]:
            continue
        ma, md = statistics.fmean(med["antes"]), statistics.fmean(med["depois"])
        m = {"chave": chave, "nome": nome, "antes": ma, "depois": md, "diferenca": md - ma,
             "em_pct": 100 * (md - ma) / ma, "divisor": divisor, "unidade": unidade,
             "vai_e_vem_antes": max(med["antes"]) - min(med["antes"]),
             "vai_e_vem_depois": max(med["depois"]) - min(med["depois"]),
             "medianas_antes": med["antes"], "medianas_depois": med["depois"],
             "pares": [d - a for a, d in zip(med["antes"], med["depois"])],
             "todas_antes": todas["antes"], "todas_depois": todas["depois"]}
        saida["medidas"].append(m)
        print(f"{nome}: antes {ma:.2f} s, depois {md:.2f} s, diferenca {md - ma:+.2f} s ({m['em_pct']:+.1f}%); "
              f"vai-e-vem antes {m['vai_e_vem_antes']:.2f} s, depois {m['vai_e_vem_depois']:.2f} s; "
              f"pares {[round(p, 2) for p in m['pares']]}")
    (AQUI / "velocidade.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
