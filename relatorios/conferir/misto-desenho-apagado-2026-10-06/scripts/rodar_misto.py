"""Roda o Misto de fabrica ("Guardar a tinta forte") de novo em cada pagina
gravada por rodar_base.py, com o codigo da worktree NA HORA (antes ou depois
do conserto), e mede o tempo (06/10/2026).

Chama core.misto.aplicar_misto com as MESMAS entradas que o programa passou
(a pagina preparada, a marcacao, as linhas do leitor e a altura delas, as
opcoes da pagina) - e a mesma chamada de core.pipeline._filtrar_no_misto, sem
rodar o detector nem o leitor de novo. Com rotulo "antes", confere que sai
ponto a ponto igual ao Misto gravado pelo programa (prova de que o atalho e o
mesmo caminho).

Uso: python rodar_misto.py antes|depois [repeticoes]
Grava <TRABALHO>/<rotulo>/<pagina>.png e <TRABALHO>/<rotulo>/tempos.json
"""

from __future__ import annotations

import gc
import json
import pickle
import sys
import time

import cv2
import numpy as np

import comum

BASE = comum.TRABALHO / "base"


def main() -> None:
    from core import misto

    rotulo = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    destino = comum.TRABALHO / rotulo
    destino.mkdir(parents=True, exist_ok=True)
    tempos = {}
    for js in sorted(BASE.glob("*.json")):
        d = json.loads(js.read_text(encoding="utf-8"))
        z = np.load(BASE / f"{js.stem}.npz")
        sel = pickle.loads((BASE / f"{js.stem}.sel.pkl").read_bytes())
        img = z["img"]
        linhas = z["linhas"] if d["tem_linhas"] else None
        o = d["opcoes"]
        ts = []
        for _ in range(reps):
            medidas: dict = {}
            t0 = time.perf_counter()
            saida, mono = misto.aplicar_misto(
                img.copy(), sel, o["forca_preto"], o["algoritmo"], o["despeckle"],
                o["clareza"], o["intensidade"], papel_da_gravura_branco=True,
                letras_na_moldura=misto.LETRAS_NA_MOLDURA_PADRAO,
                fora_do_texto=misto.FORA_REDE, linhas=linhas,
                altura_linha=d["altura_linha"], medidas=medidas)
            ts.append(time.perf_counter() - t0)
        igual = None
        if rotulo == "antes":
            igual = bool(saida.shape == z["a"].shape and np.array_equal(saida, z["a"]))
        cv2.imwrite(str(destino / f"{js.stem}.png"), saida)
        tempos[js.stem] = {"mediana_s": round(float(np.median(ts)), 3), "todos": [round(t, 3) for t in ts],
                           "igual_ao_programa": igual, "um_bit": bool(mono),
                           "medidas": {k: v for k, v in medidas.items()}}
        print(js.stem, tempos[js.stem]["mediana_s"], "igual" if igual else igual,
              {k: (round(v, 4) if isinstance(v, float) else v) for k, v in medidas.items()},
              flush=True)
        del img, z, saida
        gc.collect()
    (destino / "tempos.json").write_text(json.dumps(tempos, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
