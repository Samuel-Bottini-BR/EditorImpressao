"""Verificador 22/10, 2.6: folha de contato do arquivo de impressão (cada lado de papel, na ordem do arquivo),
com o número de página do livro que o conferir.py achou em cada metade (vermelho), para olhar a ordem e as margens.
Uso: python folhas26.py <montado.pdf> <saida.jpg> <titulo> [colunas]"""
import json
import sys
from pathlib import Path

import cv2
import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

pdf, saida, titulo = sys.argv[1], sys.argv[2], sys.argv[3]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 4
dobra = Path(pdf).with_name(Path(pdf).stem + "-dobra.json")
d = json.loads(dobra.read_text(encoding="utf-8")) if dobra.is_file() else None
f = ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf", 18)
fn = ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf", 16)
ims = []
with fitz.open(pdf) as doc:
    for n, p in enumerate(doc):
        pix = p.get_pixmap(dpi=40, alpha=False)
        a = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3).copy()
        a = cv2.copyMakeBorder(a, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=(90, 90, 90))
        im = Image.fromarray(a)
        dr = ImageDraw.Draw(im)
        if d:
            l = d["lados"][n]
            for s, x in (("esq", im.width // 4), ("dir", 3 * im.width // 4)):
                t = "branca" if not l[s] else f"p. {l[s]['pagina']}"
                dr.text((x - 25, im.height // 2 - 10), t, fill=(220, 0, 0), font=f)
            dr.line([(im.width // 2, 0), (im.width // 2, im.height)], fill=(0, 150, 255), width=1)
        cab = Image.new("RGB", (im.width, 24), "white")
        folha = n // 2 + 1
        ImageDraw.Draw(cab).text((4, 2), f"folha {folha} {'frente' if n % 2 == 0 else 'verso'} ({p.rect.width*25.4/72:.0f} x {p.rect.height*25.4/72:.0f} mm)", fill="black", font=fn)
        ims.append(np.vstack([np.asarray(cab), np.asarray(im)]))
h = max(i.shape[0] for i in ims); w = max(i.shape[1] for i in ims)
ims = [cv2.copyMakeBorder(i, 0, h - i.shape[0] + 10, 0, w - i.shape[1] + 10, cv2.BORDER_CONSTANT, value=(255, 255, 255)) for i in ims]
while len(ims) % cols:
    ims.append(np.full_like(ims[0], 255))
grade = np.vstack([np.hstack(ims[i:i + cols]) for i in range(0, len(ims), cols)])
topo = Image.new("RGB", (grade.shape[1], 60), "white")
dt = ImageDraw.Draw(topo)
dt.text((6, 4), titulo, fill="black", font=f)
if d:
    dt.text((6, 32), f"Dobra simulada (verificador): {'CERTA' if d['dobra_certa'] else 'ERRADA'} - leitura {d['leitura_depois_de_dobrar']}", fill="black", font=fn)
final = np.vstack([np.asarray(topo), grade])
cv2.imwrite(saida, cv2.cvtColor(final, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 85])
