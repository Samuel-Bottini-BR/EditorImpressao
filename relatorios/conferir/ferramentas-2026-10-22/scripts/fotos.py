"""Verificador 22/10/2026: monta as fotos de conferência a partir dos PDFs gerados (não roda o programa).

Cada foto leva no alto a frase de por onde a página passou e com quais opções (lida do .json que
caminho.py grava ao lado de cada PDF).

  python fotos.py livros  <pdf_antes> <pdf_depois> <saida.jpg> [titulo]
      as páginas lado a lado, antes numa linha e depois na outra, na MESMA escala (cm do papel)
  python fotos.py paineis <saida.jpg> <indice da página, de 1> <rótulo>=<pdf> [<rótulo>=<pdf> ...]
      a mesma página em vários PDFs, lado a lado, e embaixo o pedaço ampliado (--detalhe x0,y0,x1,y1)
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FONTE = r"C:\Windows\Fonts\segoeui.ttf"
NEGRITO = r"C:\Windows\Fonts\segoeuib.ttf"


def fonte(t=18, b=False):
    return ImageFont.truetype(NEGRITO if b else FONTE, t)


def render(pdf, i, dpi):
    with fitz.open(str(pdf)) as d:
        pix = d[i].get_pixmap(dpi=int(round(dpi)), alpha=False)
        return np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy()


def texto_em_cima(img, linhas, largura_letra=10):
    lin = []
    for k, l in enumerate(linhas):
        lin += [(w, k == 0) for w in textwrap.wrap(l, max(30, img.shape[1] // largura_letra))] or [("", False)]
    h = 8 + 26 * len(lin)
    faixa = Image.new("RGB", (img.shape[1], h), "white")
    d = ImageDraw.Draw(faixa)
    for k, (l, b) in enumerate(lin):
        d.text((6, 4 + 26 * k), l, fill="black", font=fonte(18, b))
    return np.vstack([np.asarray(faixa), img])


def juntar_h(imgs, sep=14):
    alt = max(i.shape[0] for i in imgs)
    ps = [cv2.copyMakeBorder(i, 0, alt - i.shape[0], 0, sep, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for i in imgs]
    return np.hstack(ps)


def juntar_v(imgs, sep=18):
    lar = max(i.shape[1] for i in imgs)
    ps = [cv2.copyMakeBorder(i, 0, sep, 0, lar - i.shape[1], cv2.BORDER_CONSTANT, value=(255, 255, 255)) for i in imgs]
    return np.vstack(ps)


def info(pdf):
    j = Path(pdf).with_suffix(".json")
    return json.loads(j.read_text(encoding="utf-8")) if j.is_file() else {}


def gravar(img, saida):
    Path(saida).parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(saida), cv2.cvtColor(img, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])


def livros(antes, depois, saida, titulo="", px_por_cm=14):
    linhas = []
    for rot, pdf in (("ANTES", antes), ("DEPOIS", depois)):
        inf = info(pdf)
        with fitz.open(str(pdf)) as d:
            n = d.page_count
            tam = [(p.rect.width / 72 * 2.54, p.rect.height / 72 * 2.54) for p in d]
        pags = []
        for i in range(n):
            im = render(pdf, i, px_por_cm * 2.54)
            im = cv2.copyMakeBorder(im, 2, 2, 2, 2, cv2.BORDER_CONSTANT, value=(120, 120, 120))
            pags.append(texto_em_cima(im, [f"p. {i + 1}: {tam[i][0]:.1f} x {tam[i][1]:.1f} cm"]))
        avisos = inf.get("avisos", {})
        cab = [f"{rot}: {inf.get('caminho', '')}"]
        if avisos:
            cab.append("Avisos: " + "; ".join(f"p. {k}: {', '.join(v)}" for k, v in avisos.items()))
        linha = juntar_h(pags)
        linhas.append(texto_em_cima(linha, cab, largura_letra=10))
    final = juntar_v(linhas)
    if titulo:
        final = texto_em_cima(final, [titulo])
    gravar(final, saida)


def paineis(saida, indice, pares, detalhe=None, altura=900, lado_detalhe=700):
    cols, dets = [], []
    for rot, pdf in pares:
        inf = info(pdf)
        im = render(pdf, indice - 1, 150)
        esc = altura / im.shape[0]
        peq = cv2.resize(im, (int(im.shape[1] * esc), altura), interpolation=cv2.INTER_AREA)
        if detalhe:
            x0, y0, x1, y1 = detalhe
            H, W = im.shape[:2]
            cv2.rectangle(peq, (int(x0 * peq.shape[1]), int(y0 * altura)), (int(x1 * peq.shape[1]), int(y1 * altura)),
                          (230, 0, 0), 2)
            grande = render(pdf, indice - 1, 300)
            H, W = grande.shape[:2]
            corte = grande[int(y0 * H):int(y1 * H), int(x0 * W):int(x1 * W)]
            e2 = lado_detalhe / max(corte.shape[:2])
            dets.append(texto_em_cima(cv2.resize(corte, (int(corte.shape[1] * e2), int(corte.shape[0] * e2)),
                                                 interpolation=cv2.INTER_AREA), [rot + " (ampliado, 300 DPI)"]))
        opcoes = inf.get("pagina") or {}
        frase = inf.get("caminho", "") + (" → página: " + ", ".join(f"{k}={v}" for k, v in opcoes.items()) if opcoes else "")
        cols.append(texto_em_cima(peq, [rot, frase], largura_letra=9))
    final = juntar_h(cols)
    if dets:
        final = juntar_v([final, juntar_h(dets)])
    gravar(final, saida)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="m", required=True)
    a = sub.add_parser("livros"); a.add_argument("antes"); a.add_argument("depois"); a.add_argument("saida")
    a.add_argument("titulo", nargs="?", default="")
    b = sub.add_parser("paineis"); b.add_argument("saida"); b.add_argument("indice", type=int)
    b.add_argument("pares", nargs="+"); b.add_argument("--detalhe", default="")
    o = ap.parse_args()
    if o.m == "livros":
        livros(o.antes, o.depois, o.saida, o.titulo)
    else:
        det = [float(v) for v in o.detalhe.split(",")] if o.detalhe else None
        paineis(o.saida, o.indice, [p.split("=", 1) for p in o.pares], det)


if __name__ == "__main__":
    main()
