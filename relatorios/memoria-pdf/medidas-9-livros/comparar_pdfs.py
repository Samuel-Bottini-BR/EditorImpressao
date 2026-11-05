"""Confere se o PDF do código antigo e o do novo são iguais (04/11/2026).

PARA QUE SERVE
    Pedido do Samuel (04/11/2026), medir nos 9 livros: para os livros rodados
    com o código antigo (antes do conserto da memória) e com o novo, conferir
    que o PDF de saída é o mesmo:
    1. o mesmo número de páginas;
    2. em TODAS as páginas, as imagens guardadas na página (os dados de cada
       imagem, byte a byte, e o tamanho/espaço de cor) e o desenho da página
       (o conteúdo que põe a imagem no lugar) iguais;
    3. numa amostra de páginas espalhadas (pelo menos 10: a primeira, a última e
       as do meio a intervalos iguais), a página desenhada (rasterizada) pixel a
       pixel, com o MuPDF, a 150 dpi, e também cada imagem da página
       descomprimida, comparada pixel a pixel na resolução dela.

USO: python comparar_pdfs.py ANTIGO.pdf NOVO.pdf SAIDA.json [--amostra 12]
SEGURO MUDAR: a resolução e o tamanho da amostra. Só lê os dois PDFs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import fitz
import numpy as np


def _imagens(doc: fitz.Document, i: int) -> list[dict]:
    saida = []
    for item in doc[i].get_images(full=True):
        xref = item[0]
        bruto = doc.xref_stream_raw(xref)
        saida.append({"xref": xref, "largura": item[2], "altura": item[3], "bits": item[4],
                      "cor": item[5], "filtro": item[8],
                      "sha": hashlib.sha256(bruto or b"").hexdigest()})
    return saida


def _desenho(doc: fitz.Document, i: int) -> str:
    pag = doc[i]
    h = hashlib.sha256()
    for x in pag.get_contents():
        h.update(doc.xref_stream(x) or b"")
    h.update(repr(tuple(pag.rect)).encode())
    h.update(repr(tuple(pag.mediabox)).encode())
    return h.hexdigest()


def _pixels_da_pagina(doc: fitz.Document, i: int, dpi: int) -> np.ndarray:
    pm = doc[i].get_pixmap(dpi=dpi, alpha=False)
    return np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n)


def _pixels_das_imagens(doc: fitz.Document, i: int) -> list[np.ndarray]:
    saida = []
    for item in doc[i].get_images(full=True):
        pm = fitz.Pixmap(doc, item[0])
        saida.append(np.frombuffer(pm.samples, dtype=np.uint8).reshape(pm.height, pm.width, pm.n).copy())
        pm = None
    return saida


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("antigo", type=Path)
    ap.add_argument("novo", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--amostra", type=int, default=12)
    ap.add_argument("--dpi", type=int, default=150)
    a = ap.parse_args()

    r: dict = {"antigo": str(a.antigo), "novo": str(a.novo)}
    with fitz.open(a.antigo) as da, fitz.open(a.novo) as dn:
        r["paginas_antigo"], r["paginas_novo"] = da.page_count, dn.page_count
        r["mesmo_numero_de_paginas"] = da.page_count == dn.page_count
        n = min(da.page_count, dn.page_count)

        # 2. todas as páginas: imagens (bytes) e desenho
        img_dif, des_dif, n_img = [], [], 0
        for i in range(n):
            ia, inn = _imagens(da, i), _imagens(dn, i)
            n_img += len(ia)
            chave = lambda lst: [(d["largura"], d["altura"], d["bits"], d["cor"], d["filtro"], d["sha"]) for d in lst]
            if chave(ia) != chave(inn):
                img_dif.append(i + 1)
            # o desenho cita a imagem pelo nome (/Im1...), não pelo número: compara o texto
            if _desenho(da, i) != _desenho(dn, i):
                des_dif.append(i + 1)
        r["todas_as_paginas"] = {"paginas": n, "imagens_conferidas": n_img,
                                 "paginas_com_imagem_diferente": img_dif,
                                 "paginas_com_desenho_diferente": des_dif}

        # 3. amostra espalhada, pixel a pixel
        k = min(max(a.amostra, 10), n)
        amostra = sorted({round(j * (n - 1) / (k - 1)) for j in range(k)}) if k > 1 else [0]
        r["amostra"] = []
        for i in amostra:
            pa, pn = _pixels_da_pagina(da, i, a.dpi), _pixels_da_pagina(dn, i, a.dpi)
            igual_pag = pa.shape == pn.shape and bool(np.array_equal(pa, pn))
            dif_pag = None if pa.shape != pn.shape else int(np.count_nonzero(np.any(pa != pn, axis=2)))
            ima, imn = _pixels_das_imagens(da, i), _pixels_das_imagens(dn, i)
            igual_img = len(ima) == len(imn) and all(x.shape == y.shape and np.array_equal(x, y)
                                                     for x, y in zip(ima, imn))
            r["amostra"].append({"pagina": i + 1, "tamanho_px": list(pa.shape[:2]),
                                 "pagina_desenhada_igual": igual_pag, "pixels_diferentes": dif_pag,
                                 "imagens": len(ima),
                                 "imagens_px": [list(x.shape) for x in ima],
                                 "imagens_iguais_pixel_a_pixel": igual_img})
    r["tudo_igual"] = (r["mesmo_numero_de_paginas"] and not img_dif and not des_dif
                       and all(x["pagina_desenhada_igual"] and x["imagens_iguais_pixel_a_pixel"]
                               for x in r["amostra"]))
    a.saida.parent.mkdir(parents=True, exist_ok=True)
    a.saida.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in r.items() if k != "amostra"}, ensure_ascii=False))
    print("amostra:", [(x["pagina"], x["pagina_desenhada_igual"], x["imagens_iguais_pixel_a_pixel"]) for x in r["amostra"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
