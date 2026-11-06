"""A tabela das medidas de memória para o relatório (04/11/2026).

Lê relatorios/memoria-pdf/medidas/*.json (medir_memoria.py) e imprime, em
markdown, uma linha por medida: o caminho (processar, cadernos, livreto), as
folhas, antes ou depois do conserto, o pico do programa, o tamanho do PDF e se
caiu. Uso: python relatorios/memoria-pdf/tabela_das_medidas.py
Seguro mudar: tudo (é só apresentação).
"""

from __future__ import annotations

import json
from pathlib import Path

PASTA = Path(__file__).resolve().parent / "medidas"
NOMES = {"processar": "Processar", "cadernos": "Processar + Montar cadernos",
         "livreto": "Processar + livreto (Montar para imprimir)"}


def _fase_mais_alta(dados: dict) -> str:
    fases = dados.get("pico_por_fase", {})
    if not fases:
        return "-"
    nome, valor = max(fases.items(), key=lambda kv: kv[1].get("privado_mb", 0))
    return nome


def linhas() -> list[str]:
    saida = ["| Caminho | Folhas | Código | Pico do programa | PDF | Resultado | Onde foi o pico |",
             "|---|---|---|---|---|---|---|"]
    medidas = []
    for caminho in sorted(PASTA.glob("rh-*.json")):
        _rh, folhas, modo, quando = caminho.stem.split("-")
        medidas.append((list(NOMES).index(modo), int(folhas), quando != "antes", modo, quando,
                        json.loads(caminho.read_text(encoding="utf-8"))))
    for _o, folhas, _q, modo, quando, dados in sorted(medidas):
        pico = dados["pico_total"].get("privado_mb")
        pdf = f"{dados['pdf_mb']:.0f} MB" if dados.get("pdf_mb") else "-"
        resultado = "caiu: faltou memória" if dados.get("erro") else "pronto"
        saida.append(f"| {NOMES[modo]} | {folhas} | {quando} | {pico:,} MB | {pdf} | {resultado} | "
                     f"{_fase_mais_alta(dados)} |".replace(",", "."))
    return saida


if __name__ == "__main__":
    print("\n".join(linhas()))
