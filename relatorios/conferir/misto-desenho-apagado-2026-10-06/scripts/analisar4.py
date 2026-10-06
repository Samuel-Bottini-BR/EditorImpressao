"""Quanto do que volta vem de amontoado que encosta na borda da imagem (06/10/2026)."""
import json, sys
import cv2, numpy as np
from prototipo import rede_de_hoje, BASE
c = json.load(open(BASE.parent / "comparar.json"))
for st, v in c.items():
    if v["identica"]: continue
    z = np.load(BASE / f"{st}.npz"); d = json.load(open(BASE / f"{st}.json"))
    h = d["altura_linha"]
    fora, forte, esc = rede_de_hoje(z["binaria"], z["cinza"], z["linhas"], h, z["imagem"])
    r = max(1, round(0.08 * h)); e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    n, rot, stt, _ = cv2.connectedComponentsWithStats(cv2.dilate(fora.view(np.uint8), e))
    sem = np.zeros(n, bool); sem[np.unique(rot[forte])] = True; sem[0] = False
    tot = np.bincount(rot[fora], minlength=n); apg = np.bincount(rot[fora & ~forte], minlength=n)
    ok = sem & (tot >= 0.3*h*h) & (apg >= 0.04*tot); ok[0] = False
    A, L = fora.shape; m = max(2, int(h / 4))
    x, y, w, hh = stt[:, 0], stt[:, 1], stt[:, 2], stt[:, 3]
    borda = (x <= m) | (y <= m) | (x + w >= L - m) | (y + hh >= A - m)
    lista = [(int(apg[i]), bool(borda[i]), (int(x[i]), int(y[i]), int(w[i]), int(hh[i]))) for i in np.flatnonzero(ok)]
    lista.sort(reverse=True)
    nb = sum(a for a, b, _ in lista if b); tt = sum(a for a, b, _ in lista)
    print(f"{st:28s} volta {tt:6d}  da borda {nb:6d}  ", lista[:4], (L, A))
