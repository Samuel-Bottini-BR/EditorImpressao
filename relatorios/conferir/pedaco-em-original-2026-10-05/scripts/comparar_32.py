r"""Compara ponto a ponto ANTES (19c1ba7) x AGORA (este ramo): as 32 páginas do
gabarito em Original, Preto e branco, Melhorar e Mágico pro, geradas por
rodar_32.py (o caminho do botão "Confirmar e processar"; o PDF é gravado e
lido de volta). Nenhuma delas tem pedaço marcado: tem de dar tudo idêntico
(o conserto da página em Original só vale com pedaço; o do "(2)" e o do
aviso não mexem no processamento).

Uso: comparar_32.py PASTA_DAS_RODADAS
Grava comparacao-32-paginas.json ao lado da pasta scripts\.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import cv2
import numpy as np

RODADAS = Path(sys.argv[1])
AQUI = Path(__file__).resolve().parents[1]
lista = json.loads(Path(r"D:\programas\EditorImpressao\gabarito\lista.json").read_text(encoding="utf-8"))
resultado: dict = {"antes": "19c1ba7", "agora": "este ramo (pedaco-e-salvo-2-2026-10-05)"}
for f in ("original", "preto_e_branco", "melhorar", "magico_pro"):
    por_pagina = {}
    for pid in lista["paginas"]:
        a = cv2.imread(str(RODADAS / f"antes-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        b = cv2.imread(str(RODADAS / f"agora-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        if a is None or b is None:
            por_pagina[pid] = "faltou imagem"
        elif a.shape != b.shape:
            por_pagina[pid] = f"tamanho diferente {a.shape} {b.shape}"
        else:
            dif = int(np.any(a != b, axis=-1).sum()) if a.ndim == 3 else int((a != b).sum())
            por_pagina[pid] = "identica" if dif == 0 else f"{dif} pontos diferentes"
    ta = json.loads((RODADAS / f"antes-{f}" / "tempos.json").read_text())
    tb = json.loads((RODADAS / f"agora-{f}" / "tempos.json").read_text())
    soma_a = sum(v.get("processar_s", 0) for v in ta.values())
    soma_b = sum(v.get("processar_s", 0) for v in tb.values())
    iguais = sum(v == "identica" for v in por_pagina.values())
    resultado[f] = {"identicas": iguais, "de": len(por_pagina),
                    "processar_32_paginas_s": {"antes": round(soma_a, 1), "agora": round(soma_b, 1)},
                    "paginas": por_pagina}
    print(f, iguais, "de", len(por_pagina), "identicas; processar 32 paginas: antes %.1f s, agora %.1f s"
          % (soma_a, soma_b))
    for pid, v in por_pagina.items():
        if v != "identica":
            print("   ", pid, v)
(AQUI / "comparacao-32-paginas.json").write_text(json.dumps(resultado, indent=1, ensure_ascii=False),
                                                  encoding="utf-8")
