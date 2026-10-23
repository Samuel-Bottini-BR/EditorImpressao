"""Folhear um PDF antes de escolher as caixinhas (verificador, 23/10/2026): uma folha de
contato com N folhas espalhadas pelo livro, pequenas, numeradas, para decidir "como o Kaique
pensaria" (folha dupla? torta? borda preta? amarelado? gravura?). Só lê o PDF.
Uso: python folhear.py <pdf> <saida.jpg> [n=16] [lado=360] [paginas=1,5,9 (opcional)]"""
import sys

import fitz
from PIL import Image, ImageDraw

pdf, saida = sys.argv[1], sys.argv[2]
n = int(sys.argv[3]) if len(sys.argv) > 3 else 16
lado = int(sys.argv[4]) if len(sys.argv) > 4 else 360
doc = fitz.open(pdf)
if len(sys.argv) > 5:
    indices = [int(x) - 1 for x in sys.argv[5].split(",")]
else:
    indices = sorted({round(i * (doc.page_count - 1) / max(1, n - 1)) for i in range(n)})
imgs = []
for i in indices:
    p = doc[i]
    z = lado / max(p.rect.width, p.rect.height)
    pix = p.get_pixmap(matrix=fitz.Matrix(z, z))
    im = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    imgs.append((i + 1, im))
col = 4
lin = (len(imgs) + col - 1) // col
folha = Image.new("RGB", (col * (lado + 10), lin * (lado + 30)), "white")
d = ImageDraw.Draw(folha)
for k, (num, im) in enumerate(imgs):
    x, y = (k % col) * (lado + 10), (k // col) * (lado + 30)
    folha.paste(im, (x, y + 22))
    d.text((x + 4, y + 4), f"folha {num} de {doc.page_count}", fill="black")
folha.save(saida, quality=85)
print(saida, folha.size)
