"""Escuro relativo dos pedacos que voltariam (so para escolher; 06/10/2026)."""
import json, sys
import cv2, numpy as np
from prototipo import rede_de_hoje, BASE
for st in sys.argv[1].split(","):
    z = np.load(BASE / f"{st}.npz"); d = json.load(open(BASE / f"{st}.json"))
    h = d["altura_linha"]; cinza = z["cinza"]; T = z["binaria"] == 0
    fora, forte, esc = rede_de_hoje(z["binaria"], cinza, z["linhas"], h, z["imagem"])
    dentro = T & z["linhas"]
    p10 = float(np.percentile(cinza[dentro], 10)); papel = float(np.median(cinza[~T]))
    r = max(1, round(0.08 * h)); e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    n, rot = cv2.connectedComponents(cv2.dilate(fora.view(np.uint8), e))
    sem = np.zeros(n, bool); sem[np.unique(rot[forte])] = True; sem[0] = False
    tot = np.bincount(rot[fora], minlength=n)
    ok = sem & (tot >= 0.3*h*h)
    volta = fora & ~forte & ok[rot]
    m, prot, pst, _ = cv2.connectedComponentsWithStats(volta.view(np.uint8), connectivity=8)
    pmin = np.full(m, 255.0); np.minimum.at(pmin, prot[volta], cinza[volta])
    t = (pmin - p10) / max(papel - p10, 1)
    w = pst[:, 4].astype(float); w[0] = 0
    frac = lambda lim: float(w[t <= lim].sum() / max(w.sum(), 1))
    print(f"{st:26s} esc {esc:5.0f} p10 {p10:5.0f} papel {papel:5.0f} | px {int(w.sum()):6d} "
          f"frac t<=0.3 {frac(0.3):.2f}  <=0.4 {frac(0.4):.2f} <=0.5 {frac(0.5):.2f}  shape {cinza.shape}")
