"""Medidas por amontoado devolvido (so para escolher o criterio; 06/10/2026)."""
import json, sys
import cv2, numpy as np
import comum
from prototipo import rede_de_hoje, BASE
paginas = sys.argv[1].split(",")
for st in paginas:
    z = np.load(BASE / f"{st}.npz"); d = json.load(open(BASE / f"{st}.json"))
    h = d["altura_linha"]; cinza = z["cinza"]
    fora, forte, esc = rede_de_hoje(z["binaria"], cinza, z["linhas"], h, z["imagem"])
    papel = float(np.median(cinza[z["binaria"] != 0]))
    r = max(1, round(0.08 * h)); e = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*r+1, 2*r+1))
    n, rot = cv2.connectedComponents(cv2.dilate(fora.view(np.uint8), e))
    sem = np.zeros(n, bool); sem[np.unique(rot[forte])] = True; sem[0] = False
    tot = np.bincount(rot[fora], minlength=n)
    ok = sem & (tot >= 0.3*h*h)
    apag = fora & ~forte
    # pecas apagadas
    m, prot, pst, _ = cv2.connectedComponentsWithStats(apag.view(np.uint8), connectivity=8)
    pmin = np.full(m, 255); np.minimum.at(pmin, prot[apag], cinza[apag])
    pclu = np.zeros(m, int); pclu[prot[apag]] = rot[apag]
    # sementes: maior lado das pecas fortes
    k, frot, fst, _ = cv2.connectedComponentsWithStats(forte.view(np.uint8), connectivity=8)
    fclu = np.zeros(k, int); fclu[frot[forte]] = rot[forte]
    lado = np.maximum(fst[:, 2], fst[:, 3]) / h
    out = []
    for i in np.flatnonzero(ok):
        sel = (pclu == i); sel[0] = False
        if not sel.any(): continue
        t = (pmin[sel] - esc) / max(papel - esc, 1)
        area = pst[sel, 4]
        fs = (fclu == i); fs[0] = False
        x, y, w, hh = cv2.boundingRect((rot == i).astype(np.uint8))
        dens = tot[i] / max(w*hh, 1)
        out.append((int(area.sum()), round(float(np.average(t, weights=area)), 2),
                    round(float(np.average(pmin[sel] <= esc, weights=area)), 2),
                    round(float(lado[fs].max()), 2), int(fs.sum()), round(float(tot[i]/h/h), 2),
                    round(dens, 3), (x, y, w, hh)))
    out.sort(reverse=True)
    print(st, "h", round(h), "esc", esc, "papel", papel)
    for o in out[:6]:
        print("   volta", o[0], "t_med", o[1], "escuro%", o[2], "maior_semente_h", o[3], "n_sementes", o[4], "tinta_h2", o[5], "dens", o[6], o[7])
