"""Verificador 2.1: para cada pagina do PDF de saida, acha de que folha (e de
que metade) do livro de entrada ela veio, comparando miniaturas (correlacao).
Candidatos: cada folha inteira, e as metades em 0,40..0,60 e nas posicoes dadas.
Uso: python conferir_pdf.py <entrada.pdf> <saida.pdf> <saida.json> [posicoes.json]"""
import json, sys
import fitz, numpy as np, cv2
ent, sai, out = sys.argv[1:4]
pos = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else {}
def img(pg, dpi=40):
    p = pg.get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    return np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width)
def vet(a):
    a = cv2.resize(a, (48, 64), interpolation=cv2.INTER_AREA).astype(np.float32)
    a -= a.mean(); n = np.linalg.norm(a); return a / n if n else a
E = fitz.open(ent); cand = []
for i, pg in enumerate(E):
    a = img(pg); w = a.shape[1]
    cand.append((i + 1, "inteira", vet(a)))
    ps = set([0.45, 0.5, 0.55] + [p for p in pos.get(str(i + 1), [])])
    for p in ps:
        x = int(p * w)
        cand.append((i + 1, f"esq@{p:.2f}", vet(a[:, :x]))); cand.append((i + 1, f"dir@{p:.2f}", vet(a[:, x:])))
S = fitz.open(sai); res = []
for k, pg in enumerate(S):
    v = vet(img(pg))
    sc = sorted(((float((v * c).sum()), f, m) for f, m, c in cand), reverse=True)
    melhor = sc[0]; outra = next(s for s in sc if s[1] != melhor[1])
    res.append({"pagina": k + 1, "folha": melhor[1], "parte": melhor[2], "nota": round(melhor[0], 3),
                "melhor_outra_folha": [outra[1], round(outra[0], 3)]})
json.dump(res, open(out, "w"), indent=0)
for r in res: print(r)
