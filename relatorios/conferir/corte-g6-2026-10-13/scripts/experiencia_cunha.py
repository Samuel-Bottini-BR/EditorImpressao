"""EXPERIENCIA (nao e conserto, nada do programa muda): e se a pagina fosse
endireitada, SO PARA MEDIR O CORTE, repetindo a beirada no lugar de por
branco na cunha do giro?

A suspeita (ver causa.py): na ordem nova o corte e medido na pagina girada
por core.endireitar.rotacionar, que poe BRANCO onde a pagina girada nao
cobre. Esse branco fica entre a beirada da imagem e a borda preta do
scanner, e core.recortar.detectar_bordas deixa de reconhecer a borda.

Aqui o corte e medido de tres jeitos na pagina inteira (em cinza), para as
paginas giradas do dados.json:
    "programa"   rotacionar (cunha branca) + detectar_bordas  = o livro novo
    "repetida"   mesmo giro, cunha preenchida repetindo a beirada
                 (cv2.BORDER_REPLICATE) + detectar_bordas
e a pagina final (sempre com a cunha BRANCA, como o programa desenha) e
medida com a mesma conta de faixa escura e de conteudo do medir.py.

Serve so para dizer se a suspeita explica o defeito e se a ideia vale ser
passada ao implementador. Grava experiencia-cunha.json.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[2]
FINAIS = RAIZ / "_tmp" / "finais"
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI))

import cv2  # noqa: E402
import numpy as np  # noqa: E402

import medir as M  # noqa: E402
from core.endireitar import rotacionar, rotacionar_e_cortar  # noqa: E402
from core.recortar import caixa_em_pontos, detectar_bordas  # noqa: E402


def girar_repetindo(cinza: np.ndarray, angulo: float) -> np.ndarray:
    alt, larg = cinza.shape[:2]
    matriz = cv2.getRotationMatrix2D((larg / 2.0, alt / 2.0), angulo, 1.0)
    return cv2.warpAffine(cinza, matriz, (larg, alt), flags=cv2.INTER_CUBIC,
                          borderMode=cv2.BORDER_REPLICATE)


def main() -> int:
    dados = json.loads((PASTA / "dados.json").read_text(encoding="utf-8"))
    saida = {}
    for base, d in sorted(dados.items()):
        if "C" not in d or abs(d["C"]["angulo"]) < 0.1:
            continue
        inteira = cv2.imread(str(FINAIS / f"{base}__inteira.jpg"))
        cinza = cv2.cvtColor(inteira, cv2.COLOR_BGR2GRAY)
        angulo = d["C"]["angulo"]
        pecas = M._pecas_do_conteudo(inteira)
        r = {}
        for nome, reta in (("programa", rotacionar(cinza, angulo)),
                           ("repetida", girar_repetindo(cinza, angulo))):
            recorte = detectar_bordas(reta, dpi=M.DPI).tupla
            caixa = caixa_em_pontos(inteira.shape, recorte)
            final = rotacionar_e_cortar(inteira, angulo, caixa) if caixa else rotacionar(inteira, angulo)
            m = M._medir_a_beirada(final)
            c = M._medir_o_conteudo(pecas, recorte, angulo, True, True)
            r[nome] = {"recorte": [round(float(v), 4) for v in recorte],
                       "tamanho_mm": [round(final.shape[1] * 25.4 / M.DPI, 1), round(final.shape[0] * 25.4 / M.DPI, 1)],
                       "beirada_escuro": m["beirada_escuro"], "tinta_perdida": c["tinta_perdida"],
                       "pecas_partidas": c["pecas_partidas"], "pecas_fora": c["pecas_fora"],
                       "cunha_branca": M._cunha_branca(inteira.shape, recorte, angulo, True, True)}
        r["antiga_B"] = {k: d["B"][k] for k in ("tamanho_mm", "beirada_escuro", "tinta_perdida",
                                                 "pecas_partidas", "pecas_fora", "cunha_branca")}
        r["nova_C_do_programa"] = {k: d["C"][k] for k in ("recorte", "tamanho_mm", "beirada_escuro")}
        saida[base] = r
        p, q, b = r["programa"], r["repetida"], r["antiga_B"]
        print(f"{base:30s} faixa: antiga {100 * b['beirada_escuro']:5.2f}%  nova {100 * p['beirada_escuro']:5.2f}%  "
              f"repetida {100 * q['beirada_escuro']:5.2f}%   tinta fora: {100 * b['tinta_perdida']:.2f} "
              f"{100 * p['tinta_perdida']:.2f} {100 * q['tinta_perdida']:.2f}   "
              f"tamanho: {b['tamanho_mm']} {p['tamanho_mm']} {q['tamanho_mm']}", flush=True)
    (PASTA / "experiencia-cunha.json").write_text(json.dumps(saida, indent=1, ensure_ascii=False),
                                                  encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
