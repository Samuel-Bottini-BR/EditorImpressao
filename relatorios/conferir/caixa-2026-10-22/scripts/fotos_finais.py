"""Verificador 22/10: as fotos que vao para a Central.
1) egenloff_p003_etiqueta_perto.jpg: a etiqueta de baixo e os carimbos de cima, antes | depois, ampliados.
2) avisos_o_que_fica_fora.jpg: o que o aviso "Corte deixou algo de fora" esta contando, em 6 paginas
   (retangulo azul POR FORA de cada peca contada; vermelho = o que o corte tira).
Uso: python fotos_finais.py (rodar na pasta caixa-2026-10-22)"""
import json
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

F = ImageFont.truetype("arialbd.ttf", 30); f = ImageFont.truetype("arial.ttf", 24)
CAM = "Caminho: não precisou dividir -> endireitada -> cortada (cortar pelo conteúdo + borda preta até a moldura) -> filtro Original, 300 DPI"


def verm(img, caixa):
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    fora = np.ones(g.shape, bool); x0, y0, x1, y1 = caixa; fora[max(0, y0):y1, max(0, x0):x1] = False
    v = np.zeros_like(img); v[..., 2] = 255; v[..., 1] = (g * 205).astype(np.uint8); v[..., 0] = v[..., 1]
    out = img.copy(); out[fora] = v[fora]; return out


def pil(b): return Image.fromarray(cv2.cvtColor(b, cv2.COLOR_BGR2RGB))


def caber(im, w): return im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def rot(im, t, alto=44, cor=(150, 0, 0)):
    o = Image.new("RGB", (im.width, im.height + alto), "white"); o.paste(im, (0, alto))
    ImageDraw.Draw(o).text((6, 6), t, fill=cor, font=F); return o


def grade(linhas, sep=14):
    w = max(sum(i.width for i in l) + sep * (len(l) - 1) for l in linhas)
    h = sum(max(i.height for i in l) for l in linhas) + sep * (len(linhas) - 1)
    o = Image.new("RGB", (w, h), "white"); y = 0
    for l in linhas:
        x = 0
        for i in l: o.paste(i, (x, y)); x += i.width + sep
        y += max(i.height for i in l) + sep
    return o


def cabeca(im, linhas):
    alto = 14 + 36 * len(linhas); o = Image.new("RGB", (im.width, im.height + alto), "white")
    d = ImageDraw.Draw(o)
    for k, (t, fo) in enumerate(linhas): d.text((10, 8 + 36 * k), t, fill=(0, 0, 0) if fo is F else (60, 60, 60), font=fo)
    o.paste(im, (0, alto)); return o


# 1) Egenloff 3
lados = {}
for lado, rotulo in (("antes", "ANTES (c66f28d)"), ("novo", "DEPOIS (49d1ed3)")):
    info = json.load(open(f"trabalho/cap_egenloff_{lado}_info.json", encoding="utf-8"))["3"]
    lados[lado] = (verm(cv2.imread(f"trabalho/cap_egenloff_{lado}_p003_reta.png"), info["caixa"]), rotulo)
partes = []
for nome, (y0, y1, x0, x1) in (("embaixo: a etiqueta \"1880 neu aufgelegt von George Gilbers\"", (4250, 5000, 500, 4100)),
                               ("em cima: o carimbo oval e o lápis \"Af 10\"", (150, 800, 1100, 3400)),
                               ("à direita: o carimbo \"Fachschule für angewandte Kunst\"", (800, 1700, 3200, 4150))):
    linha = [rot(caber(pil(lados[l][0][y0:y1, x0:x1]), 880), f"{lados[l][1]} - {nome.split(':')[0]}") for l in ("antes", "novo")]
    partes.append(linha)
im = cabeca(grade(partes), [("Egenloff, página 3 (folha de rosto): as beiradas, ampliadas", F), (CAM, f),
                           ("Preto = fica no papel. Vermelho = o programa tirou.", f),
                           ("Linha 1: a etiqueta de baixo. Linha 2: o carimbo de cima. Linha 3: o carimbo da direita.", f)])
im.save("img/egenloff_p003_beiradas_perto.jpg", quality=86)

# 2) o que o aviso conta
casos = [("egenloff", 3, "Egenloff 3: risco de caneta do carimbo e o fim de \"Schneeberg\""),
         ("egenloff", 6, "Egenloff 6: o verso por transparência e a faixa da biblioteca"),
         ("marial", 8, "Marial 8: três pontinhos e um risco na beirada do papel"),
         ("marial", 10, "Marial 10: a sombra da beirada do papel grudada no texto"),
         ("marial", 28, "Marial 28: mancha e beirada do papel grudadas no texto"),
         ("marial", 43, "Marial 43: a beirada do papel e a borda do escaneado")]
fj = {l: json.load(open(f"trabalho/fora_{l}_fora.json", encoding="utf-8")) for l in ("egenloff", "marial")}
ims = []
for l, n, t in casos:
    b = cv2.imread(f"trabalho/fora_{l}_p{n:03d}_fora.png")
    for p in fj[l][str(n)]["tiradas"]:
        cv2.rectangle(b, (p["x0"] - 30, p["y0"] - 30), (p["x1"] + 30, p["y1"] + 30), (255, 60, 0), 16)
    ims.append(rot(caber(pil(b), 560), t, alto=40, cor=(0, 0, 0)))
for i in ims: ImageDraw.Draw(i)
small = []
for i in ims:
    o = Image.new("RGB", (i.width, i.height), "white"); o.paste(i, (0, 0)); small.append(o)
# titulo de cada uma em fonte menor, quebrado
fin = []
for (l, n, t), i in zip(casos, ims):
    o = Image.new("RGB", (i.width, i.height + 30), "white"); o.paste(i.crop((0, 40, i.width, i.height)), (0, 70))
    d = ImageDraw.Draw(o); pal = t.split(": ")
    d.text((4, 4), pal[0], fill=(0, 0, 0), font=F); d.text((4, 40), pal[1], fill=(60, 60, 60), font=ImageFont.truetype("arial.ttf", 19))
    fin.append(o)
im = cabeca(grade([fin[:3], fin[3:]]), [("O que o aviso \"Corte deixou algo de fora\" está contando (depois, 49d1ed3)", F), (CAM, f),
                                         ("Vermelho = o corte tira. Retângulo azul = cada pedaço que o aviso contou como \"ficou de fora\".", f)])
im.save("img/avisos_o_que_fica_fora.jpg", quality=86)
print("ok")
