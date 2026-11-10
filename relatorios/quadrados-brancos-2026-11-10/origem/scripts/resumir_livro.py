"""Resume o livro inteiro (rodar_livro.sh + medir.py): por situacao e filtro, quantas paginas com
pintura tem buracos brancos, e a ligacao com a gravura achada (a ideia do Samuel: onde o motor do
ScanTailor acha a gravura, nao ha quadrados).

    python resumir_livro.py <pasta de trabalho> <saida.json>
"""
import json
import sys
from pathlib import Path

T = Path(sys.argv[1])
med = json.loads((T / "medidas_livro.json").read_text(encoding="utf-8"))
res = {}
for sit in ("antes", "hoje", "desfeita"):
    for filtro in ("melhorar", "magico_pro"):
        m = med[f"livro/{sit}:{filtro}"]
        g = json.loads((T / "livro" / sit / f"{filtro}.json").read_text(encoding="utf-8"))
        com_pintura = {p: v for p, v in m.items() if v.get("tem_pintura")}
        visiveis = sorted(int(p) for p, v in com_pintura.items() if v["buraco_pintura_pct"] >= 6)
        algum = sorted(int(p) for p, v in com_pintura.items() if v["buraco_pintura_pct"] >= 2)
        achou = {int(p) for p, v in g.items() if p != "_como" and v["gravuras_achadas"] > 0}
        sem_gravura_com_pintura = sorted(int(p) for p in com_pintura if int(p) not in achou)
        r = {
            "paginas": len(m), "com_pintura": len(com_pintura),
            "gravura_achada_em": len(achou),
            "buracos_bem_visiveis_6pct": visiveis,
            "buracos_2pct": algum,
            "pintura_sem_gravura_achada": sem_gravura_com_pintura,
            "buraco_onde_achou": sorted(p for p in visiveis if p in achou),
            "buraco_onde_nao_achou": sorted(p for p in visiveis if p not in achou),
            "letra_quebrada_paginas_1pct": sorted(int(p) for p, v in m.items() if v["tinta_sumida_pct"] >= 1),
            "papel_sujo_paginas_2pct": sorted(int(p) for p, v in m.items() if v.get("papel_sujo_pct", 0) >= 2),
            "segundos_media": round(sum(v["segundos"] for p, v in g.items() if p != "_como")
                                    / max(1, len(g) - 1), 2),
        }
        res[f"{sit}:{filtro}"] = r
        print(sit, filtro, {k: (len(v) if isinstance(v, list) else v) for k, v in r.items()})
Path(sys.argv[2]).write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
