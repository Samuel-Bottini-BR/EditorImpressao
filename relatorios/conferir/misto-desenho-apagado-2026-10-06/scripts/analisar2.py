"""Forma dos pedacos que voltariam (so para escolher o criterio; 06/10/2026)."""
import json, sys
import cv2, numpy as np
from prototipo import rede_de_hoje, BASE
for st in sys.argv[1].split(","):
    z = np.load(BASE / f"{st}.npz"); d = json.load(open(BASE / f"{st}.json"))
    h = d["altura_linha"]; cinza = z["cinza"]
    fora, forte, esc = rede_de_hoje(z["binaria"], cinza, z["linhas"], h, z["imagem"])
    r = max(1, round(0.08 * h)); e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    n, rot = cv2.connectedComponents(cv2.dilate(fora.view(np.uint8), e))
    sem = np.zeros(n, bool); sem[np.unique(rot[forte])] = True; sem[0] = False
    tot = np.bincount(rot[fora], minlength=n)
    ok = sem & (tot >= 0.3*h*h)
    volta = fora & ~forte & ok[rot]
    m, prot, pst, _ = cv2.connectedComponentsWithStats(volta.view(np.uint8), connectivity=8)
    lado = np.maximum(pst[:, 2], pst[:, 3]).astype(float); area = pst[:, 4].astype(float)
    along = lado**2 / np.maximum(area, 1)       # traco fino: grande; grao/borrao: perto de 1-2
    grande = lado / h
    w = area[1:]
    def q(x): return [round(float(v), 2) for v in np.percentile(x, [25, 50, 75])]
    print(f"{st:26s} n {m-1:5d} px {int(w.sum()):6d} along(p25,50,75) {q(along[1:])} lado/h {q(grande[1:])}"
          f" frac_along>=4 {float(w[along[1:]>=4].sum()/max(w.sum(),1)):.2f} frac_lado>=h/4 {float(w[grande[1:]>=0.25].sum()/max(w.sum(),1)):.2f}")
