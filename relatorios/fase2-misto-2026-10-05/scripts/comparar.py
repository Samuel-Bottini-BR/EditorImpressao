"""Compara duas rodadas do caminho_atual.py: imagens idênticas? tempo?

Uso: python comparar.py antes depois   (lê dados/caminho-atual-<rotulo>.json)
Imprime as páginas/filtros com imagem diferente (nenhuma é o esperado) e a
soma dos tempos de cada filtro nas duas rodadas.
"""

from __future__ import annotations

import json
import sys

import comum


def main() -> None:
    a_rot, b_rot = sys.argv[1], sys.argv[2]
    a = json.loads((comum.PASTA / "dados" / f"caminho-atual-{a_rot}.json").read_text(encoding="utf-8"))
    b = json.loads((comum.PASTA / "dados" / f"caminho-atual-{b_rot}.json").read_text(encoding="utf-8"))
    diferentes, iguais = [], 0
    tempos = {}
    for pid in sorted(set(a) | set(b)):
        for filtro, va in a.get(pid, {}).items():
            if not isinstance(va, dict):
                continue
            vb = b.get(pid, {}).get(filtro)
            if vb is None or vb["somas"] != va["somas"]:
                diferentes.append(f"{pid} {filtro}")
            else:
                iguais += len(va["somas"])
            t = tempos.setdefault(filtro, [0.0, 0.0])
            t[0] += va["s"]
            t[1] += vb["s"] if vb else 0.0
    print(f"imagens identicas: {iguais}; diferentes: {len(diferentes)}")
    for d in diferentes:
        print("  DIFERENTE:", d)
    for filtro, (ta, tb) in tempos.items():
        print(f"{filtro}: {a_rot} {ta:.1f} s, {b_rot} {tb:.1f} s ({100 * (tb - ta) / ta:+.1f}%)")


if __name__ == "__main__":
    main()
