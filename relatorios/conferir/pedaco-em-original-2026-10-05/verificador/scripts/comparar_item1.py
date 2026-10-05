"""Item 1 (verificador, rodada 2, 05/10): pagina em Original com pedaco em Preto e branco.

janela-item1.pdf  = gerado na janela real (consertos3, 17d705b), pedaco na p.1
antes-item1.pdf   = o mesmo projeto pelo 19c1ba7 (pedaco ignorado = Original puro)
Mede: dentro do retangulo, quantos tons; fora, pontos diferentes do Original.
Grava recortes para olhar.
"""
import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

C = Path(sys.argv[1])
proj = json.loads((C / "projeto-item1.json").read_text(encoding="utf-8"))


def imagens(pdf):
    out = []
    with fitz.open(pdf) as d:
        for p in d:
            ims = p.get_images(full=True)
            xref = ims[0][0]
            pix = fitz.Pixmap(d, xref)
            info = {"canais": pix.n, "cor": pix.colorspace.name if pix.colorspace else None,
                    "imagens": len(ims), "bytes": len(d.xref_stream_raw(xref))}
            if pix.colorspace is None or pix.n not in (1, 3):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n).copy()
            a = np.repeat(a, 3, axis=2) if a.shape[2] == 1 else a[:, :, ::-1]
            out.append((a, info))
    return out


jan = imagens(C / "janela-item1.pdf")
ant = imagens(C / "antes-item1.pdf")
res = {"paginas": {}}
for i in range(len(jan)):
    a, ia = jan[i]
    b, ib = ant[i]
    linha = {"janela": ia, "19c1ba7": ib, "mesmo_tamanho": a.shape == b.shape}
    if a.shape == b.shape:
        linha["pontos_diferentes"] = int(np.any(a != b, axis=2).sum())
    res["paginas"][i + 1] = linha

# pagina 1: o retangulo do pedaco
pag = proj["paginas"][0]
sel = pag.get("selecao") or []
ret = [r for r in sel if r.get("forma") == "retangulo" and r.get("filtro")][-1]
(x0, y0), (x1, y1) = ret["pontos"]
a, _ = jan[0]
b, _ = ant[0]
h, w = a.shape[:2]
X0, Y0, X1, Y1 = int(round(x0 * w)), int(round(y0 * h)), int(round(x1 * w)), int(round(y1 * h))
dentro = np.zeros((h, w), bool)
dentro[Y0:Y1, X0:X1] = True
dif = np.any(a != b, axis=2)
borda = np.zeros((h, w), bool)
borda[max(0, Y0 - 3):Y1 + 3, max(0, X0 - 3):X1 + 3] = True
borda &= ~np.pad(np.ones((max(0, Y1 - Y0 - 6), max(0, X1 - X0 - 6)), bool),
                 ((Y0 + 3, h - Y1 + 3), (X0 + 3, w - X1 + 3)))[:h, :w]
inner = a[Y0 + 3:Y1 - 3, X0 + 3:X1 - 3].reshape(-1, 3)
tons = np.unique(inner, axis=0)
res["pagina1"] = {
    "retangulo_fracoes": ret["pontos"], "filtro_do_pedaco": ret["filtro"], "filtro_da_pagina": pag.get("filtro"),
    "retangulo_px": [X0, Y0, X1, Y1], "imagem_px": [w, h],
    "tons_dentro_(sem_3px_da_beira)": int(len(tons)), "exemplos_de_tons": tons[:6].tolist(),
    "fora_pontos_diferentes_do_original": int((dif & ~dentro & ~borda).sum()),
    "fora_inclusive_beira_3px": int((dif & ~dentro).sum()),
    "dentro_pontos_diferentes": int((dif & dentro).sum()), "dentro_total": int(dentro.sum()),
}
print(json.dumps(res, indent=1, ensure_ascii=False))
(C / "comparacao-item1.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")

# imagens para olhar
esc = 1100 / h
lado = np.hstack([cv2.resize(b, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA),
                  np.zeros((int(round(h * esc)), 8, 3), np.uint8) + 255,
                  cv2.resize(a, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)])
cv2.imwrite(str(C / "item1-pagina-antes-x-janela.jpg"), lado, [cv2.IMWRITE_JPEG_QUALITY, 85])
# beirada de baixo do retangulo, perto do tamanho real
yy0, yy1 = max(0, Y1 - 250), min(h, Y1 + 250)
xx0, xx1 = X0, min(w, X0 + 900)
cv2.imwrite(str(C / "item1-beirada-baixo.jpg"),
            np.hstack([b[yy0:yy1, xx0:xx1], np.full((yy1 - yy0, 8, 3), 255, np.uint8), a[yy0:yy1, xx0:xx1]]),
            [cv2.IMWRITE_JPEG_QUALITY, 88])
# titulo
cv2.imwrite(str(C / "item1-titulo.jpg"),
            np.vstack([b[Y0:Y0 + 420, X0:X1], np.full((8, X1 - X0, 3), 255, np.uint8), a[Y0:Y0 + 420, X0:X1]]),
            [cv2.IMWRITE_JPEG_QUALITY, 88])
