"""Le o experiencia.json e escreve, para cada variante pedida, so as paginas
em que o corte mudou em relacao ao programa de hoje ("b"), com a regra do
verificador (classificar.py): piorou se a faixa escura cresceu 0,5 ponto ou
mais, ou a tinta de fora 0,1 ponto ou mais, ou as pecas partidas + de fora 2
ou mais; melhorou no contrario.

USO  python comparar_exp.py variante[,variante...]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PASTA = Path(__file__).resolve().parent.parent


def classe(a: dict, n: dict) -> str:
    d_faixa = n["beirada_escuro"] - a["beirada_escuro"]
    d_tinta = n["tinta_perdida"] - a["tinta_perdida"]
    d_pecas = (n["pecas_partidas"] + n["pecas_fora"]) - (a["pecas_partidas"] + a["pecas_fora"])
    pior = d_faixa >= 0.005 or d_tinta >= 0.001 or d_pecas >= 2
    melhor = d_faixa <= -0.005 or d_tinta <= -0.001 or d_pecas <= -2
    return "PIOROU" if pior else ("melhorou" if melhor else "igual")


def main() -> int:
    exp = json.loads((PASTA / "experiencia.json").read_text(encoding="utf-8"))
    if sys.argv[1] == "--lados":      # --lados variantes paginas: a faixa por lado, em mm
        for base in sys.argv[3].split(","):
            for v in sys.argv[2].split(","):
                q = exp[base][v]
                print(f"{base:28s} {v:6s} recorte {q['recorte']}  faixa por lado (mm) {q['lados_mm']}  "
                      f"folga {q['folga_mm']}")
        return 0
    for v in sys.argv[1].split(","):
        print(f"\n=== {v} contra o programa de hoje (b); entre parenteses, a ordem antiga (B)")
        mudou = 0
        for base, r in sorted(exp.items()):
            if v not in r or "b" not in r:
                continue
            a, n, B = r["b"], r[v], r["antiga_B"]
            if a["recorte"] == n["recorte"]:
                continue
            mudou += 1
            print(f"  {base:30s} {classe(a, n):8s} faixa {100 * a['beirada_escuro']:5.2f} -> {100 * n['beirada_escuro']:5.2f} "
                  f"({100 * B['beirada_escuro']:5.2f})  tinta fora {100 * a['tinta_perdida']:.2f} -> {100 * n['tinta_perdida']:.2f} "
                  f"({100 * B['tinta_perdida']:.2f})  pecas {a['pecas_partidas']}+{a['pecas_fora']} -> "
                  f"{n['pecas_partidas']}+{n['pecas_fora']}  mm {a['tamanho_mm'][0]:.0f}x{a['tamanho_mm'][1]:.0f} -> "
                  f"{n['tamanho_mm'][0]:.0f}x{n['tamanho_mm'][1]:.0f}  contra B: {classe(B, n)}")
        print(f"  ({mudou} paginas com o corte diferente do de hoje)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
