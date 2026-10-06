"""Tempo do Misto de fabrica antes e depois do conserto, no MESMO processo,
alternando as duas versoes em cada pagina (06/10/2026). A versao antiga e o
core/misto.py do commit b6e0a0e (gravado em trabalho/misto_antigo.py).
Uso: python tempo.py [repeticoes]   (grava trabalho/tempo.json)"""
import importlib.util, json, pickle, sys, time
import numpy as np
import comum
from core import misto as novo
spec = importlib.util.spec_from_file_location("misto_antigo", comum.TRABALHO / "misto_antigo.py")
antigo = importlib.util.module_from_spec(spec); sys.modules["misto_antigo"] = antigo; spec.loader.exec_module(antigo)
reps = int(sys.argv[1]) if len(sys.argv) > 1 else 5
B = comum.TRABALHO / "base"; res = {}
for js in sorted(B.glob("*.json")):
    d = json.loads(js.read_text(encoding="utf-8")); z = np.load(B / f"{js.stem}.npz")
    sel = pickle.loads((B / f"{js.stem}.sel.pkl").read_bytes()); img = z["img"]
    lin = z["linhas"] if d["tem_linhas"] else None; o = d["opcoes"]
    t = {"antes": [], "depois": []}
    for _ in range(reps):
        for nome, mod in (("antes", antigo), ("depois", novo)):
            t0 = time.perf_counter()
            mod.aplicar_misto(img, sel, o["forca_preto"], o["algoritmo"], o["despeckle"], o["clareza"],
                              o["intensidade"], papel_da_gravura_branco=True, fora_do_texto=mod.FORA_REDE,
                              linhas=lin, altura_linha=d["altura_linha"], medidas={})
            t[nome].append(time.perf_counter() - t0)
    res[js.stem] = {k: round(float(np.median(v)), 3) for k, v in t.items()}
    res[js.stem]["megapixels"] = round(img.shape[0] * img.shape[1] / 1e6, 1)
    print(js.stem, res[js.stem], flush=True)
a = sum(v["antes"] for v in res.values()); b = sum(v["depois"] for v in res.values())
res["_total"] = {"antes": round(a, 2), "depois": round(b, 2), "aumento_pct": round(100 * (b - a) / a, 1)}
print(res["_total"])
(comum.TRABALHO / "tempo.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
