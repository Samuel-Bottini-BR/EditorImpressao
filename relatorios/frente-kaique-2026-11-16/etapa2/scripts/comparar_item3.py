"""Etapa 2, item 3: compara o projeto e o PDF do programa de 28/10 com os do programa empacotado de hoje.

1. projeto.json: o que o programa de 28/10 gravou x o que o de hoje gravou depois de abrir e processar
   (campo por campo: no livro, em cada folha e em cada página). Campos novos (que o de 28/10 não tinha)
   vão numa lista à parte, com o valor.
2. PDF: número de páginas, tamanho de cada página e a imagem de cada página (diferença média de pixel,
   a 60 DPI, em tons de cinza), e uma folha lado a lado das páginas que mudaram.

Uso: .venv\\Scripts\\python.exe comparar_item3.py <pasta etapa2> <pdf antes> <pdf depois> <saida>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw

W, PDF_ANTES, PDF_DEPOIS, SAIDA = map(Path, sys.argv[1:5])
SAIDA.mkdir(parents=True, exist_ok=True)
REL = "EditorImpressao/projetos/righetti-14-folhas/projeto.json"
antes = json.loads((W / "antigo" / "dados" / REL).read_text(encoding="utf-8"))
depois = json.loads((W / "novo3" / "dados" / REL).read_text(encoding="utf-8"))

linhas: list[str] = []
novos: dict[str, object] = {}


def comparar(a, b, onde):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a:
                novos.setdefault(f"{onde.split('[')[0]}.{k}", b[k])
            elif k not in b:
                linhas.append(f"SUMIU  {onde}.{k} (era {json.dumps(a[k], ensure_ascii=False)[:120]})")
            else:
                comparar(a[k], b[k], f"{onde}.{k}")
    elif isinstance(a, list) and isinstance(b, list) and len(a) == len(b) and a and isinstance(a[0], dict):
        for i, (x, y) in enumerate(zip(a, b)):
            comparar(x, y, f"{onde}[{i}]")
    elif a != b:
        linhas.append(f"MUDOU  {onde}: {json.dumps(a, ensure_ascii=False)[:160]}  ->  "
                      f"{json.dumps(b, ensure_ascii=False)[:160]}")


comparar(antes, depois, "projeto")
texto = ["# projeto.json: 28/10 x hoje", "",
         f"folhas: {len(antes.get('folhas', []))} -> {len(depois.get('folhas', []))}; "
         f"páginas: {len(antes.get('paginas', []))} -> {len(depois.get('paginas', []))}", "",
         f"## Valores que mudaram ou sumiram ({len(linhas)})", ""] + linhas + [
         "", f"## Campos novos que o de hoje acrescentou ({len(novos)}; valor da primeira vez)", ""] + [
         f"NOVO   {k} = {json.dumps(v, ensure_ascii=False)[:160]}" for k, v in sorted(novos.items())]
(SAIDA / "projeto-comparado.txt").write_text("\n".join(texto), encoding="utf-8")
print("\n".join(texto[:6]))
print(f"mudaram/sumiram: {len(linhas)}; novos: {len(novos)}")

# --- o PDF
da, dd = fitz.open(PDF_ANTES), fitz.open(PDF_DEPOIS)
res = {"paginas_antes": da.page_count, "paginas_depois": dd.page_count, "paginas": []}


def cinza(doc, i, dpi=60):
    p = doc[i].get_pixmap(dpi=dpi, colorspace=fitz.csGRAY)
    return np.frombuffer(p.samples, np.uint8).reshape(p.height, p.width)


mudadas = []
for i in range(min(da.page_count, dd.page_count)):
    ra, rd = da[i].rect, dd[i].rect
    a, b = cinza(da, i), cinza(dd, i)
    if a.shape == b.shape:
        dif = float(np.abs(a.astype(int) - b.astype(int)).mean())
        px = float((np.abs(a.astype(int) - b.astype(int)) > 40).mean() * 100)
    else:
        dif, px = None, None
    item = {"pagina": i + 1, "tamanho_antes": [round(ra.width, 1), round(ra.height, 1)],
            "tamanho_depois": [round(rd.width, 1), round(rd.height, 1)],
            "diferenca_media": None if dif is None else round(dif, 2),
            "pct_pixels_bem_diferentes": None if px is None else round(px, 2)}
    res["paginas"].append(item)
    if dif is None or dif > 1.0:
        mudadas.append(i)
(SAIDA / "pdf-comparado.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"PDF: {da.page_count} -> {dd.page_count} folhas do PDF; mudaram (dif média > 1): {[i + 1 for i in mudadas]}")
for it in res["paginas"]:
    print(it)


def faixa(doc, idx, titulo, cor):
    ims = []
    for i in idx:
        p = doc[i].get_pixmap(dpi=45)
        ims.append(Image.frombytes("RGB", (p.width, p.height), p.samples))
    larg = sum(x.width for x in ims) + 12 * (len(ims) + 1)
    alt = max(x.height for x in ims) + 70
    c = Image.new("RGB", (larg, alt), cor)
    d = ImageDraw.Draw(c)
    d.text((12, 8), titulo, fill="white")
    x = 12
    for i, im in zip(idx, ims):
        d.text((x, 30), f"folha {i + 1} do PDF", fill="white")
        c.paste(im, (x, 50))
        x += im.width + 12
    return c


# folha de comparação: as 4 primeiras folhas do PDF (onde estão as páginas mexidas à mão) e as que mudaram
mostrar = sorted(set(list(range(min(4, da.page_count))) + mudadas[:4]))
fa = faixa(da, mostrar, "ANTES - PDF do programa de 28/10", (40, 90, 170))
fd = faixa(dd, mostrar, "DEPOIS - o mesmo projeto aberto e processado no programa empacotado de hoje", (40, 140, 70))
c = Image.new("RGB", (max(fa.width, fd.width), fa.height + fd.height + 10), "white")
c.paste(fa, (0, 0)); c.paste(fd, (0, fa.height + 10))
c.save(SAIDA / "pdf-antes-depois.png")
print("ok", SAIDA / "pdf-antes-depois.png")
