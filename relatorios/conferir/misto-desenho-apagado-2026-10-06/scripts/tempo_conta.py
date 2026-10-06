"""Custo so da conta nova (core.misto._desenho_colado_a_tinta_forte) em cada
pagina, o menor de 5 voltas (06/10/2026). Grava trabalho/tempo_conta.json."""
import json, time
import numpy as np
import comum
from core import misto
from prototipo import rede_de_hoje, BASE
res = {}
for js in sorted(BASE.glob("*.json")):
    d = json.loads(js.read_text(encoding="utf-8"))
    if not d["tem_linhas"]:
        res[js.stem] = 0.0; continue
    z = np.load(BASE / f"{js.stem}.npz"); h = d["altura_linha"]
    fora, forte, esc = rede_de_hoje(z["binaria"], z["cinza"], z["linhas"], h, z["imagem"])
    if esc is None or esc <= misto.LETRA_SEM_TONS:
        res[js.stem] = 0.0; continue
    ts = []
    for _ in range(5):
        t0 = time.perf_counter(); misto._desenho_colado_a_tinta_forte(fora, forte, h); ts.append(time.perf_counter() - t0)
    res[js.stem] = round(min(ts), 3)
v = list(res.values())
res["_resumo"] = {"maior_s": max(v), "mediana_s": float(np.median(v)), "soma_s": round(sum(v), 2)}
print(res["_resumo"]); print(sorted(((b, a) for a, b in res.items() if a != "_resumo"), reverse=True)[:5])
(comum.TRABALHO / "tempo_conta.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
