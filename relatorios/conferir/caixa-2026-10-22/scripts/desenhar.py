"""Verificador, 22/10/2026: as fotos da conferencia (antes c66f28d x depois 49d1ed3) a partir do que o
capturar_corte.py gravou. Regra das fotos do Samuel: nada desenhado por cima do conteudo; o que FICA no papel
aparece como esta; o que o programa TIRA aparece em vermelho; a parte ampliada e marcada na folha inteira com
amarelo transparente. Duas imagens por pagina:
  <nome>__perto.jpg : em cima a folha inteira (antes | depois), pequena, com a faixa ampliada em amarelo;
                      embaixo cada beirada que mudou, ampliada, antes em cima e depois embaixo.
  <nome>__inteira.jpg: a pagina inteira antes | depois, grande.
Uso: python desenhar.py <pasta trabalho> <livro: egenloff|marial> <pagina> <titulo> <caminho e opcoes> <saida img>"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

trab, livro, n, titulo, caminho, saida = sys.argv[1:7]
n = int(n)
trab, saida = Path(trab), Path(saida)
F = ImageFont.truetype("arialbd.ttf", 26)
f = ImageFont.truetype("arial.ttf", 22)


def carregar(lado):
    info = json.loads((trab / f"cap_{livro}_{lado}_info.json").read_text(encoding="utf-8"))[str(n)]
    img = cv2.imread(str(trab / f"cap_{livro}_{lado}_p{n:03d}_reta.png"))
    return img, info


def tirar_em_vermelho(img, caixa):
    """Fora da caixa: a tinta vira vermelha e o papel rosa claro. Dentro: como esta."""
    g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    fora = np.ones(g.shape, bool)
    if caixa is not None:
        x0, y0, x1, y1 = caixa
        fora[max(0, y0):y1, max(0, x0):x1] = False
    out = img.copy()
    verm = np.zeros_like(img)
    verm[..., 2] = 255
    verm[..., 1] = (g * 205).astype(np.uint8)
    verm[..., 0] = (g * 205).astype(np.uint8)
    out[fora] = verm[fora]
    return out


def amarelo(img, faixas):
    out = img.copy().astype(np.float32)
    for (y0, y1, x0, x1) in faixas:
        reg = out[y0:y1, x0:x1]
        reg[...] = reg * 0.6 + np.array([0, 230, 255], np.float32) * 0.4
    return out.astype(np.uint8)


def rotulo(im, texto, fonte=F, cor=(170, 0, 0), alto=40):
    t = Image.new("RGB", (im.width, im.height + alto), "white")
    t.paste(im, (0, alto))
    ImageDraw.Draw(t).text((8, 6), texto, fill=cor, font=fonte)
    return t


def pil(bgr):
    return Image.fromarray(cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB))


def lado_a_lado(ims, sep=16):
    h = max(i.height for i in ims)
    t = Image.new("RGB", (sum(i.width for i in ims) + sep * (len(ims) - 1), h), "white")
    x = 0
    for i in ims:
        t.paste(i, (x, 0)); x += i.width + sep
    return t


def empilhar(ims, sep=12):
    w = max(i.width for i in ims)
    t = Image.new("RGB", (w, sum(i.height for i in ims) + sep * (len(ims) - 1)), "white")
    y = 0
    for i in ims:
        t.paste(i, (0, y)); y += i.height + sep
    return t


def cabeca(im, linhas):
    alto = 12 + 34 * len(linhas)
    t = Image.new("RGB", (im.width, im.height + alto), "white")
    d = ImageDraw.Draw(t)
    for k, (txt, fonte, cor) in enumerate(linhas):
        d.text((10, 8 + 34 * k), txt, fill=cor, font=fonte)
    t.paste(im, (0, alto))
    return t


def caber(im, larg):
    if im.width <= larg:
        return im
    return im.resize((larg, round(im.height * larg / im.width)), Image.LANCZOS)


a, ia = carregar("antes")
b, ib = carregar("novo")
assert a.shape == b.shape, (a.shape, b.shape)
H, W = a.shape[:2]
ca, cb = ia["caixa"], ib["caixa"]
va, vb = tirar_em_vermelho(a, ca), tirar_em_vermelho(b, cb)

# as beiradas que mudaram (mais de 5 pontos = 0,4 mm a 300 DPI)
faixas = []
nomes = ["esquerda", "em cima", "direita", "embaixo"]
mudou = []
for k in range(4):
    if abs(ca[k] - cb[k]) > 5:
        mudou.append(nomes[k])
        meio_a, meio_b = sorted((ca[k], cb[k]))
        if k in (1, 3):     # horizontal: faixa da largura toda
            y0, y1 = max(0, meio_a - 260), min(H, meio_b + 260)
            faixas.append((y0, y1, 0, W))
        else:
            x0, x1 = max(0, meio_a - 260), min(W, meio_b + 260)
            faixas.append((0, H, x0, x1))

legenda = ("Preto = fica no papel. Vermelho = o programa tirou. Amarelo = a parte ampliada embaixo.")
pequena = [rotulo(caber(pil(amarelo(v, faixas)), 520), r) for v, r in ((va, "ANTES (c66f28d)"), (vb, "DEPOIS (49d1ed3)"))]
partes = [lado_a_lado(pequena)]
for (y0, y1, x0, x1), nome in zip(faixas, mudou):
    za = rotulo(caber(pil(va[y0:y1, x0:x1]), 1400), f"ANTES - a beirada {nome}, ampliada")
    zb = rotulo(caber(pil(vb[y0:y1, x0:x1]), 1400), f"DEPOIS - a beirada {nome}, ampliada")
    partes.append(lado_a_lado([za, zb]) if (x1 - x0) < (y1 - y0) else empilhar([za, zb]))
perto = cabeca(empilhar(partes, sep=24), [(titulo, F, (0, 0, 0)), (caminho, f, (60, 60, 60)), (legenda, f, (60, 60, 60))])
perto = caber(perto, 1800)
saida.parent.mkdir(parents=True, exist_ok=True)
perto.save(str(saida) + "__perto.jpg", quality=86)

grande = lado_a_lado([rotulo(caber(pil(v), 900), r) for v, r in ((va, "ANTES (c66f28d)"), (vb, "DEPOIS (49d1ed3)"))])
grande = cabeca(grande, [(titulo + " - a página inteira", F, (0, 0, 0)), (caminho, f, (60, 60, 60)),
                         ("Preto = fica no papel. Vermelho = o programa tirou.", f, (60, 60, 60))])
grande.save(str(saida) + "__inteira.jpg", quality=86)
print(saida, "mudou:", mudou, "caixas", ca, cb, "avisos antes", ia["avisos"], "depois", ib["avisos"])
