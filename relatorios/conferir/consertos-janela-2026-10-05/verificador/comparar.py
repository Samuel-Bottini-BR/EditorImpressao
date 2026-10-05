r"""Compara ponto a ponto ANTES (aab746f) x AGORA (120e46b): 32 paginas x 3
filtros. Grava comparacao-verificador.json e tempos da Horas 11."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

V = Path(__file__).resolve().parent
S = V / "rodadas"
lista = json.loads(Path(r"D:\programas\EditorImpressao\gabarito\lista.json").read_text(encoding="utf-8"))
filtros = sys.argv[1:] or ["preto_e_branco", "magico_pro", "melhorar"]
res = {}
for f in filtros:
    res[f] = {}
    for pid in lista["paginas"]:
        a = cv2.imread(str(S / f"antes-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        b = cv2.imread(str(S / f"agora-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        if a is None or b is None:
            res[f][pid] = "faltou imagem"
            continue
        if a.shape != b.shape:
            res[f][pid] = f"tamanho diferente {a.shape} {b.shape}"
            continue
        dif = int(np.any(a != b, axis=-1).sum()) if a.ndim == 3 else int((a != b).sum())
        res[f][pid] = "identica" if dif == 0 else f"{dif} pontos diferentes"
    iguais = sum(v == "identica" for v in res[f].values())
    ta = json.loads((S / f"antes-{f}" / "tempos.json").read_text())
    tb = json.loads((S / f"agora-{f}" / "tempos.json").read_text())
    print(f, iguais, "de", len(res[f]), "identicas;",
          "Horas 11 processar: antes %.1fs agora %.1fs" % (ta["horas_p011"]["processar_s"], tb["horas_p011"]["processar_s"]),
          "| soma 32 pags: antes %.0fs agora %.0fs" % (sum(v.get("processar_s", 0) for v in ta.values()),
                                                         sum(v.get("processar_s", 0) for v in tb.values())))
    for pid, v in res[f].items():
        if v != "identica":
            print("  ", pid, v)
(V / f"comparacao-{'-'.join(filtros)}.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
