"""Verificador, 21/10: mede cada pagina de um PDF gerado (mm) e faz uma folha com as paginas pequenas lado a lado.
Uso: medir_pdf.py <pdf> <folha.jpg>"""
import sys

import fitz
from PIL import Image

d = fitz.open(sys.argv[1])
ims, tam = [], []
for i, p in enumerate(d):
    w, h = round(p.rect.width / 72 * 25.4, 1), round(p.rect.height / 72 * 25.4, 1)
    tam.append((i + 1, w, h))
    pix = p.get_pixmap(dpi=24)
    ims.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
print(tam)
H = max(i.height for i in ims)
W = sum(i.width + 8 for i in ims[:7])
t = Image.new("RGB", (W, 2 * H + 8), (255, 0, 255))
x = 0
for k, i in enumerate(ims):
    if k == 7:
        x = 0
    t.paste(i, (x, 0 if k < 7 else H + 8)); x += i.width + 8
t.save(sys.argv[2], quality=88)
