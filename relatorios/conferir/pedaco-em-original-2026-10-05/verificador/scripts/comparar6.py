"""Verificador (05/10, rodada 2): 6 paginas x 4 filtros, ANTES (19c1ba7) x AGORA (17d705b),
pelo caminho do "Confirmar e processar" (rodar_32.py do implementador). Ponto a ponto.
Grava comparacao-6x4.json e uma folha de contato (agora) para olhar."""
import json
import sys
from pathlib import Path

import cv2
import numpy as np

R = Path(sys.argv[1])
IDS = ["escola_p007", "opusmajus_p020", "horas_p011", "palatino_p057", "graduale_p221", "siebmacher_p007"]
FIL = ["original", "preto_e_branco", "melhorar", "magico_pro"]
res = {"antes": "19c1ba7", "agora": "17d705b (pedaco-e-salvo-2-2026-10-05)", "filtros": {}}
linhas = []
for f in FIL:
    pp = {}
    ta = json.loads((R / f"antes-{f}" / "tempos.json").read_text())
    tb = json.loads((R / f"agora-{f}" / "tempos.json").read_text())
    miniaturas = []
    for pid in IDS:
        a = cv2.imread(str(R / f"antes-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        b = cv2.imread(str(R / f"agora-{f}" / f"{pid}.png"), cv2.IMREAD_UNCHANGED)
        if a is None or b is None:
            pp[pid] = "faltou imagem"
        elif a.shape != b.shape:
            pp[pid] = f"tamanho diferente {a.shape} {b.shape}"
        else:
            d = int(np.any(a != b, axis=-1).sum()) if a.ndim == 3 else int((a != b).sum())
            pp[pid] = "identica" if d == 0 else f"{d} pontos diferentes"
        if b is not None:
            bb = b if b.ndim == 3 else cv2.cvtColor(b, cv2.COLOR_GRAY2BGR)
            esc = 360 / bb.shape[0]
            m = cv2.resize(bb, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)
            caixa = np.full((380, 300, 3), 255, np.uint8)
            m = m[:, :300]
            caixa[:m.shape[0], :m.shape[1]] = m
            cv2.putText(caixa, f"{pid} {f}"[:34], (4, 376), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (0, 0, 200), 1)
            miniaturas.append(caixa)
    linhas.append(np.hstack(miniaturas))
    sa = sum(v.get("processar_s", 0) for v in ta.values())
    sb = sum(v.get("processar_s", 0) for v in tb.values())
    res["filtros"][f] = {"identicas": sum(v == "identica" for v in pp.values()), "de": len(pp),
                         "processar_6_s": {"antes": round(sa, 1), "agora": round(sb, 1)}, "paginas": pp}
    print(f, res["filtros"][f]["identicas"], "de", len(pp), "| processar: antes %.1f s, agora %.1f s" % (sa, sb))
    for k, v in pp.items():
        if v != "identica":
            print("   ", k, v)
(R / "comparacao-6x4.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
cv2.imwrite(str(R / "folha-de-contato-agora.jpg"), np.vstack(linhas), [cv2.IMWRITE_JPEG_QUALITY, 85])
