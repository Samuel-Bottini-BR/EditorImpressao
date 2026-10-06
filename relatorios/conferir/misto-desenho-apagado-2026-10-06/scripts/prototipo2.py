"""Variante v8 (so para medir): v7 + o pedaco que volta precisa ser "tinta media"
(o ponto mais escuro dele ate limiar = p10 da letra + FRACAO*(papel - p10)),
e nada volta em pagina sem tons de cinza (scan ja em preto e branco).
Uso: python prototipo2.py fracao [pid,...]"""
import json, sys
import cv2, numpy as np
import comum
from prototipo import rede_de_hoje, BASE
fr = float(sys.argv[1]); razao = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; so = sys.argv[2].split(",") if len(sys.argv) > 2 and sys.argv[2] != "todas" else None
dest = comum.TRABALHO / "prototipo" / f"v8_{fr}_{razao}"; dest.mkdir(parents=True, exist_ok=True)
for js in sorted(BASE.glob("*.json")):
    if so and js.stem not in so: continue
    z = np.load(BASE / f"{js.stem}.npz"); d = json.load(open(js))
    h = d["altura_linha"]
    if not d["tem_linhas"]: continue
    cinza = z["cinza"]; T = z["binaria"] == 0
    fora, forte, esc = rede_de_hoje(z["binaria"], cinza, z["linhas"], h, z["imagem"])
    if esc is None: continue
    dentro = T & z["linhas"]
    p10 = float(np.percentile(cinza[dentro], 10)); papel = float(np.median(cinza[~T]))
    if esc <= 5:
        print(js.stem, "sem tons de cinza: nada volta"); continue
    lim = p10 + fr * (papel - p10)
    r = max(1, round(0.08 * h)); e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    n, rot = cv2.connectedComponents(cv2.dilate(fora.view(np.uint8), e))
    sem = np.zeros(n, bool); sem[np.unique(rot[forte])] = True; sem[0] = False
    tot = np.bincount(rot[fora], minlength=n)
    apg = np.bincount(rot[fora & ~forte], minlength=n)
    ok = sem & (tot >= 0.3*h*h) & (apg >= razao * tot)
    cand = fora & ~forte & ok[rot]
    m, prot = cv2.connectedComponents(cand.view(np.uint8), connectivity=8)
    pmin = np.full(m, 255.0); np.minimum.at(pmin, prot[cand], cinza[cand])
    fica = pmin <= lim; fica[0] = False
    volta = cand & fica[prot]
    print(f"{js.stem:28s} volta {int(volta.sum()):6d} de {int(cand.sum()):6d}")
    if volta.any():
        a = z["a"]; a3 = cv2.cvtColor(a, cv2.COLOR_GRAY2BGR) if a.ndim == 2 else a.copy()
        a3[volta] = (255, 120, 0); a3[cand & ~volta] = (0, 0, 255)
        cv2.imwrite(str(dest / f"{js.stem}.png"), a3)
