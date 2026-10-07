"""Verificador 2.1: de que folha (e de que lado) veio cada pagina do PDF de saida.
Casa pontos (ORB) da pagina com cada folha do livro de entrada, a 80 DPI; o lado
sai da posicao x media dos pontos casados na folha (fracao da largura).
Uso: python conferir_pdf_orb.py <entrada.pdf> <saida.pdf> <saida.json>"""
import json, sys
import fitz, numpy as np, cv2
ent, sai, out = sys.argv[1:4]
orb = cv2.ORB_create(4000)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)
def img(pg, dpi=80):
    p = pg.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    return np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width)
E = fitz.open(ent); F = []
for pg in E:
    a = img(pg); k, d = orb.detectAndCompute(a, None); F.append((a.shape[1], k, d))
S = fitz.open(sai); res = []
for n, pg in enumerate(S):
    a = img(pg); k, d = orb.detectAndCompute(a, None)
    notas = []
    for i, (w, kf, df) in enumerate(F):
        if d is None or df is None: notas.append((0, i, None)); continue
        ms = bf.knnMatch(d, df, k=2)
        bons = [m for m, *r in ms if r and m.distance < 0.75 * r[0].distance]
        if len(bons) >= 8:
            src = np.float32([k[m.queryIdx].pt for m in bons]); dst = np.float32([kf[m.trainIdx].pt for m in bons])
            H, mask = cv2.estimateAffinePartial2D(src, dst, method=cv2.RANSAC, ransacReprojThreshold=4)
            inl = int(mask.sum()) if mask is not None else 0
            xs = dst[mask.ravel() == 1][:, 0] / w if inl else []
            # extensao da pagina na folha: onde vao parar os cantos da pagina
            if H is not None:
                h0, w0 = a.shape
                cantos = cv2.transform(np.float32([[[0, 0]], [[w0, 0]], [[0, h0]], [[w0, h0]]]), H)[:, 0, 0] / w
                ext = (round(float(cantos.min()), 3), round(float(cantos.max()), 3))
            else:
                ext = None
            notas.append((inl, i, ext))
        else:
            notas.append((len(bons), i, None))
    notas.sort(reverse=True)
    b = notas[0]
    res.append({"pagina": n + 1, "folha": b[1] + 1, "pontos": b[0], "faixa_da_folha": b[2], "segunda": [notas[1][1] + 1, notas[1][0]]})
json.dump(res, open(out, "w"), indent=0)
for r in res: print(r)
