"""Quanto o conserto acrescenta por pagina (nao e o teste_velocidade.py).

Mede so a busca do corte na pagina ja endireitada, como a pipeline faz no
livro novo: core.recortar.detectar_bordas(reta, dpi=300) sem e com `girada`,
nas paginas que giram (copias JPEG a 300 DPI do verificador, so leitura).
Para cada pagina, o menor de 5 tempos de cada jeito. O custo so existe uma
vez por pagina (quando a geometria e guardada) e so em pagina que gira.

USO  python custo.py     (grava custo.json nesta pasta)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
PASTA = AQUI.parent
RAIZ = PASTA.parents[1]
FINAIS = RAIZ.parent / "verif-corte-g6" / "_tmp" / "finais"
sys.path.insert(0, str(RAIZ))

import cv2  # noqa: E402

from core import recortar as R  # noqa: E402
from core.endireitar import rotacionar  # noqa: E402


def menor(funcao, vezes: int = 5) -> float:
    tempos = []
    for _ in range(vezes):
        t0 = time.perf_counter()
        funcao()
        tempos.append(time.perf_counter() - t0)
    return min(tempos) * 1000.0


def main() -> int:
    dados = json.loads((PASTA / "dados-verificador.json").read_text(encoding="utf-8"))
    saida = {}
    for base, d in sorted(dados.items()):
        if "C" not in d or abs(d["C"]["angulo"]) < 0.1:
            continue
        cinza = cv2.imread(str(FINAIS / f"{base}__inteira.jpg"), cv2.IMREAD_GRAYSCALE)
        angulo = d["C"]["angulo"]
        giro = menor(lambda: rotacionar(cinza, angulo), 3)
        reta = rotacionar(cinza, angulo)
        sem = menor(lambda: R.detectar_bordas(reta, dpi=300))
        com = menor(lambda: R.detectar_bordas(reta, dpi=300, girada=angulo))
        # a segunda conta do limiar local rodou? (so com fundo escuro perto da cunha)
        esc = R.ALTURA_ANALISE / reta.shape[0]
        cz = cv2.resize(reta, (max(8, int(reta.shape[1] * esc)), R.ALTURA_ANALISE), interpolation=cv2.INTER_AREA)
        cunha = R._cunha_do_giro(cz.shape, angulo)
        falsa = R._tinta_falsa_da_cunha(cz, R._mascara_de_tinta_local(cz), cunha)
        saida[base] = {"px": [int(cinza.shape[1]), int(cinza.shape[0])], "giro_da_pagina_ms": round(giro, 1),
                       "corte_sem_ms": round(sem, 1), "corte_com_ms": round(com, 1),
                       "a_mais_ms": round(com - sem, 1), "tinha_tinta_falsa": falsa is not None}
        print(f"{base:30s} {cinza.shape[1]}x{cinza.shape[0]}  giro {giro:6.1f} ms  corte sem {sem:6.1f}  "
              f"com {com:6.1f}  a mais {com - sem:5.1f} ms  tinta falsa: {falsa is not None}", flush=True)
    a_mais = sorted(v["a_mais_ms"] for v in saida.values())
    resumo = {"paginas": len(a_mais), "a_mais_mediana_ms": a_mais[len(a_mais) // 2],
              "a_mais_maior_ms": a_mais[-1], "a_mais_menor_ms": a_mais[0],
              "corte_sem_mediana_ms": sorted(v["corte_sem_ms"] for v in saida.values())[len(a_mais) // 2],
              "giro_mediana_ms": sorted(v["giro_da_pagina_ms"] for v in saida.values())[len(a_mais) // 2]}
    print(resumo)
    (PASTA / "custo.json").write_text(json.dumps({"resumo": resumo, "paginas": saida}, indent=1,
                                                 ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
