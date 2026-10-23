"""Recorta um print bruto, desenha quadros numerados por cima e põe a legenda embaixo (PIL).
Os prints brutos ficam fora do git (D:\\programas\\EditorImpressao-arquivos\\mapa-do-programa-prints\\brutos);
os recortados e legendados vão para relatorios/testes-guiados/mapa-do-programa/prints (JPG).

recortar(bruto, destino, caixa, legenda, marcas=[((x0,y0,x1,y1), "1"), ...], largura=1100)
  caixa e marcas em pixels do print bruto (a janela de 1536 x 800 pontos sai 1920 x 1000 px)."""
from __future__ import annotations

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

VERMELHO = (230, 40, 40)


def _fonte(tamanho: int):
    for nome in ("segoeui.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(nome, tamanho)
        except OSError:
            continue
    return ImageFont.load_default()


def recortar(bruto: Path, destino: Path, caixa, legenda: str, marcas=(), largura: int = 1100) -> Path:
    img = Image.open(bruto).convert("RGB")
    if caixa is None:
        caixa = (0, 0, img.width, img.height)
    desenho = ImageDraw.Draw(img)
    f_num = _fonte(26)
    for (x0, y0, x1, y1), rotulo in marcas:
        desenho.rectangle((x0, y0, x1, y1), outline=VERMELHO, width=4)
        if rotulo:
            tx, ty = x0, max(0, y0 - 34)
            if ty < caixa[1]:
                ty = y1 + 4
            l = desenho.textlength(rotulo, font=f_num)
            desenho.rectangle((tx, ty, tx + l + 14, ty + 32), fill=VERMELHO)
            desenho.text((tx + 7, ty + 1), rotulo, fill="white", font=f_num)
    img = img.crop(caixa)
    if img.width > largura:
        img = img.resize((largura, round(img.height * largura / img.width)), Image.LANCZOS)
    f_leg = _fonte(20)
    linhas = []
    for par in legenda.split("\n"):
        linhas += textwrap.wrap(par, width=max(40, img.width // 10)) or [""]
    alto = 16 + 27 * len(linhas)
    final = Image.new("RGB", (img.width, img.height + alto), "white")
    final.paste(img, (0, 0))
    d = ImageDraw.Draw(final)
    for i, linha in enumerate(linhas):
        d.text((12, img.height + 8 + 27 * i), linha, fill=(20, 20, 20), font=f_leg)
    destino.parent.mkdir(parents=True, exist_ok=True)
    final.save(destino, quality=85)
    return destino


def lado_a_lado(partes, destino: Path, legenda: str, altura: int = 700, largura_max: int = 1400,
                fundo=(255, 255, 255)) -> Path:
    """Junta vários recortes lado a lado (mesma altura), com um título curto em cima de cada um.
    partes: [(imagem_ou_caminho, caixa_ou_None, "título"), ...]."""
    f_tit = _fonte(22)
    imgs = []
    for fonte, caixa, titulo in partes:
        im = (Image.open(fonte) if not isinstance(fonte, Image.Image) else fonte).convert("RGB")
        if caixa:
            im = im.crop(caixa)
        im = im.resize((max(1, round(im.width * altura / im.height)), altura), Image.LANCZOS)
        imgs.append((im, titulo))
    total = sum(i.width for i, _ in imgs) + 12 * (len(imgs) + 1)
    folha = Image.new("RGB", (total, altura + 50), fundo)
    d = ImageDraw.Draw(folha)
    x = 12
    for im, titulo in imgs:
        d.text((x, 10), titulo, fill=(20, 20, 20), font=f_tit)
        folha.paste(im, (x, 44))
        x += im.width + 12
    if folha.width > largura_max:
        folha = folha.resize((largura_max, round(folha.height * largura_max / folha.width)), Image.LANCZOS)
    tmp = destino.with_suffix(".tmp.png")
    folha.save(tmp)
    recortar(tmp, destino, None, legenda, largura=largura_max)
    tmp.unlink()
    return destino
