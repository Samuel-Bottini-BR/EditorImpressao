"""Compara, ponto a ponto, as paginas dos PDFs gerados (verificador, 05/10).

Le a imagem gravada em cada pagina (como ela esta no PDF), e:
- paginas 2..10: janela (consertos2, com pedaco na p.1) x 044a7c1 x sem pedaco;
- pagina 1: janela x sem janela; dentro do pedaco x a pagina em Original;
  fora do pedaco x 044a7c1.
Grava recortes .png para olhar.
"""
import json
import os
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np

C = Path(sys.argv[1])
RAIZ = Path(r"D:\programas\EditorImpressao\.claude\worktrees\consertos2")
os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["LOCALAPPDATA"] = str(C / "_local_cmp")
sys.path.insert(0, str(RAIZ))
os.chdir(RAIZ)


def imagens(pdf):
    out = []
    with fitz.open(pdf) as d:
        for p in d:
            ims = p.get_images(full=True)
            xref = ims[0][0]
            pix = fitz.Pixmap(d, xref)
            info = (pix.n, pix.colorspace.name if pix.colorspace else None, len(ims),
                    len(d.xref_stream_raw(xref)))
            if pix.colorspace is None or pix.n not in (1, 3):
                pix = fitz.Pixmap(fitz.csRGB, pix)
            a = np.frombuffer(pix.samples, np.uint8).reshape(pix.h, pix.w, pix.n).copy()
            if a.shape[2] == 1:
                a = np.repeat(a, 3, axis=2)
            else:
                a = a[:, :, ::-1]  # RGB -> BGR
            out.append((a, info))
    return out


janela = imagens(C / "com-pedaco-consertos2.pdf")
semjan = imagens(C / "com-pedaco-consertos2-semjanela.pdf")
antes = imagens(C / "com-pedaco-044a7c1.pdf")
sem = imagens(C / "sem-pedaco-consertos2.pdf")
res = {"paginas": {}}
for i in range(len(janela)):
    a, ia = janela[i]
    linha = {"janela_info(n,cor,imagens,bytes)": ia, "044a7c1_info": antes[i][1], "sem_pedaco_info": sem[i][1]}
    for nome, outra in (("igual_sem_janela", semjan), ("igual_044a7c1", antes), ("igual_sem_pedaco", sem)):
        b = outra[i][0]
        linha[nome] = bool(a.shape == b.shape and np.array_equal(a, b))
        if a.shape == b.shape and not linha[nome]:
            linha[nome + "_pontos_diferentes"] = int(np.any(a != b, axis=2).sum())
    res["paginas"][i + 1] = linha

# pagina 1: dentro x Original, fora x 044a7c1
from core import pipeline  # noqa: E402
from core.filtros import ORIGINAL  # noqa: E402
from core.pdf_io import abrir_pdf  # noqa: E402
from core.selecao import MAO  # noqa: E402
from modelos import Projeto  # noqa: E402

projeto = Projeto.de_dicionario(json.loads((C / "projeto-com-pedaco.json").read_text(encoding="utf-8")))
pg = projeto.paginas[0]
sel = pg.obter_selecao()
reg = [r for r in sel.regioes if r.origem == MAO][0]
(fx0, fy0), (fx1, fy1) = reg.pontos[0], reg.pontos[-1]
doc = abrir_pdf(projeto.caminho_entrada)
pg.filtro = ORIGINAL
orig, _ = pipeline.renderizar_pagina(doc, projeto, pg, dpi=projeto.qualidade_dpi)
doc.close()
a = janela[0][0]
h, w = a.shape[:2]
res["pagina1"] = {"tamanho_janela": [w, h], "tamanho_original": list(orig.shape[1::-1]),
                  "pedaco_fracao": [fx0, fy0, fx1, fy1]}
if orig.shape[:2] == a.shape[:2]:
    m = np.zeros((h, w), bool)
    peso = sel.peso_do_filtro(h, w, ORIGINAL)
    m = peso >= 0.999
    dif = np.abs(a.astype(int) - orig.astype(int)).max(axis=2)
    res["pagina1"]["dentro_igual_ao_original_fracao"] = float((dif[m] == 0).mean())
    res["pagina1"]["dentro_diferenca_max"] = int(dif[m].max())
    res["pagina1"]["dentro_ate_2_niveis_fracao"] = float((dif[m] <= 2).mean())
    fora = peso <= 0.001
    b = antes[0][0]
    if b.shape == a.shape:
        d2 = np.any(a != b, axis=2)
        res["pagina1"]["fora_pontos_diferentes_de_044a7c1"] = int(d2[fora].sum())
        res["pagina1"]["fora_total_pontos"] = int(fora.sum())
        res["pagina1"]["borda_suave_pontos"] = int(((peso > 0.001) & (peso < 0.999)).sum())
    x0, y0, x1, y1 = int(fx0 * w), int(fy0 * h), int(fx1 * w), int(fy1 * h)
    pad = 60
    cv2.imwrite(str(C / "p1-janela.png"), a)
    cv2.imwrite(str(C / "p1-044a7c1.png"), antes[0][0])
    cv2.imwrite(str(C / "p1-original.png"), orig)
    for nome, img in (("janela", a), ("044a7c1", antes[0][0]), ("original", orig)):
        cv2.imwrite(str(C / f"p1-beirada-cima-{nome}.png"),
                    img[max(0, y0 - pad):y0 + 160, max(0, x0 - pad):min(w, x0 + 700)])
        cv2.imwrite(str(C / f"p1-pedaco-{nome}.png"), img[max(0, y0 - pad):min(h, y1 + pad), max(0, x0 - pad):min(w, x1 + pad)])
    res["pagina1"]["retangulo_px"] = [x0, y0, x1, y1]
print(json.dumps(res, indent=1, ensure_ascii=False))
(C / "comparacao.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
