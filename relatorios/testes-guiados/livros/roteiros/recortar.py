"""Print pequeno para o git (verificador, 23/10/2026): recorta (opcional), reduz e grava em JPG.
Com dois arquivos e "lado", põe os dois lado a lado (antes | depois) com uma legenda curta em cima.
Uso: python recortar.py <entrada> <saida.jpg> [x0,y0,x1,y1 | -] [largura=1100] [legenda]
     python recortar.py lado <a> <b> <saida.jpg> <legenda_a> <legenda_b> [altura=600]"""
import sys

from PIL import Image, ImageDraw, ImageFont


def fonte(t=22):
    try:
        return ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", t)
    except OSError:
        return ImageFont.load_default()


if sys.argv[1] == "lado":
    a, b, saida, la, lb = sys.argv[2:7]
    alt = int(sys.argv[7]) if len(sys.argv) > 7 else 600
    ims = []
    for f in (a, b):
        im = Image.open(f).convert("RGB")
        ims.append(im.resize((round(im.width * alt / im.height), alt)))
    w = ims[0].width + ims[1].width + 30
    tela = Image.new("RGB", (w, alt + 40), "white")
    d = ImageDraw.Draw(tela)
    x = 0
    for im, leg in zip(ims, (la, lb)):
        tela.paste(im, (x, 40))
        d.text((x + 6, 6), leg, fill="black", font=fonte())
        x += im.width + 30
    tela.save(saida, quality=72)
else:
    ent, saida = sys.argv[1], sys.argv[2]
    im = Image.open(ent).convert("RGB")
    if len(sys.argv) > 3 and sys.argv[3] != "-":
        im = im.crop(tuple(int(v) for v in sys.argv[3].split(",")))
    larg = int(sys.argv[4]) if len(sys.argv) > 4 else 1100
    if im.width > larg:
        im = im.resize((larg, round(im.height * larg / im.width)))
    im.save(saida, quality=72)
print(saida)
