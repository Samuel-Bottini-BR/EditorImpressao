"""Folhas de contato das imagens do implementador (so para o verificador abrir todas). Uso: folhas.py <pasta> <saida> <por folha> <largura>"""
import glob
import os
import sys

from PIL import Image, ImageDraw, ImageFont

fs = sorted(glob.glob(os.path.join(sys.argv[1], "*.jpg")))
n, W = int(sys.argv[3]), int(sys.argv[4])
F = ImageFont.truetype("arialbd.ttf", 20)
for k in range(0, len(fs), n):
    ims = [Image.open(x).convert("RGB") for x in fs[k:k + n]]
    ims = [i.resize((W, round(i.height * W / i.width))) for i in ims]
    t = Image.new("RGB", (W, sum(i.height + 26 for i in ims)), "white")
    d = ImageDraw.Draw(t); y = 0
    for i, nome in zip(ims, fs[k:k + n]):
        d.text((4, y + 2), os.path.basename(nome), fill="red", font=F); t.paste(i, (0, y + 26)); y += i.height + 26
    t.save(f"{sys.argv[2]}-{k // n + 1}.jpg", quality=82)
    print(f"{sys.argv[2]}-{k // n + 1}.jpg", t.size)
